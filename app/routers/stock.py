from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.i18n import get_lang, get_t, translate_category
from app.models import Category, Item, StockStatus, clean_name, name_key

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ctx(request: Request, **extra) -> dict:
    lang = get_lang(request)
    return {"request": request, "t": get_t(request), "lang": lang,
            "translate_category": lambda cat: translate_category(cat, lang), **extra}


def parse_category_id(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None


def get_stock_items(db: Session):
    out_of_stock = db.query(Item).filter(Item.status == StockStatus.out_of_stock).order_by(Item.name).all()
    running_low = db.query(Item).filter(Item.status == StockStatus.running_low).order_by(Item.name).all()
    normal = db.query(Item).filter(Item.status == StockStatus.normal).order_by(Item.name).all()
    return out_of_stock, running_low, normal


def validate_item_name(request: Request, db: Session, name: str, exclude_id: int | None = None) -> PlainTextResponse | None:
    """Return a 4xx response with a translated message if the name is empty or already taken."""
    t = get_t(request)
    if not clean_name(name):
        return PlainTextResponse(t["error_empty_name"], status_code=422)
    query = db.query(Item).filter(Item.name_key == name_key(name))
    if exclude_id is not None:
        query = query.filter(Item.id != exclude_id)
    existing = query.first()
    if existing:
        return duplicate_response(request, existing.name)
    return None


def duplicate_response(request: Request, name: str) -> PlainTextResponse:
    return PlainTextResponse(get_t(request)["error_duplicate_item"].format(name=name), status_code=409)


@router.get("/stock", response_class=HTMLResponse)
async def stock_page(request: Request, db: Session = Depends(get_db)):
    out_of_stock, running_low, normal = get_stock_items(db)
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "stock.html",
        ctx(request, out_of_stock=out_of_stock, running_low=running_low, normal=normal, categories=categories),
    )


@router.post("/stock/items", response_class=HTMLResponse)
async def add_stock_item(
    request: Request,
    name: str = Form(...),
    category_id: str | None = Form(None),
    status: StockStatus = Form(StockStatus.normal),
    db: Session = Depends(get_db),
):
    if error := validate_item_name(request, db, name):
        return error
    item = Item(name=name.strip(), category_id=parse_category_id(category_id), status=status)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return duplicate_response(request, clean_name(name))
    out_of_stock, running_low, normal = get_stock_items(db)
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "partials/stock_list.html",
        ctx(request, out_of_stock=out_of_stock, running_low=running_low, normal=normal, categories=categories),
    )


@router.patch("/stock/items/{item_id}/status", response_class=HTMLResponse)
async def update_stock_status(
    request: Request,
    item_id: int,
    status: StockStatus = Form(...),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.status = status
        db.commit()
    out_of_stock, running_low, normal = get_stock_items(db)
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "partials/stock_list.html",
        ctx(request, out_of_stock=out_of_stock, running_low=running_low, normal=normal, categories=categories),
    )


@router.delete("/stock/items/{item_id}", response_class=HTMLResponse)
async def delete_stock_item(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    out_of_stock, running_low, normal = get_stock_items(db)
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "partials/stock_list.html",
        ctx(request, out_of_stock=out_of_stock, running_low=running_low, normal=normal, categories=categories),
    )


@router.post("/stock/items/{item_id}/edit", response_class=HTMLResponse)
async def edit_stock_item(
    request: Request,
    item_id: int,
    name: str = Form(...),
    category_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        if error := validate_item_name(request, db, name, exclude_id=item.id):
            return error
        item.name = name.strip()
        item.category_id = parse_category_id(category_id)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return duplicate_response(request, clean_name(name))
    out_of_stock, running_low, normal = get_stock_items(db)
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "partials/stock_list.html",
        ctx(request, out_of_stock=out_of_stock, running_low=running_low, normal=normal, categories=categories),
    )
