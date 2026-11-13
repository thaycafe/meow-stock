import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.i18n import get_lang, get_t, translate_category
from app.models import Category, Item, StockStatus, clean_name, name_key
from app.services import duplicate_response, group_by_category, name_conflict
from app.templating import render

router = APIRouter()


def parse_category_id(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None


def stock_context(request: Request, db: Session) -> dict:
    lang = get_lang(request)
    categories = db.query(Category).all()
    return {
        "groups": group_by_category(db.query(Item).all(), lang),
        "categories": sorted(categories, key=lambda c: name_key(translate_category(c, lang))),
    }


def render_stock_list(request: Request, db: Session):
    return render(request, db, "partials/stock_list.html", **stock_context(request, db))


@router.get("/stock", response_class=HTMLResponse)
async def stock_page(request: Request, db: Session = Depends(get_db)):
    return render(request, db, "stock.html", **stock_context(request, db))


@router.post("/stock/items", response_class=HTMLResponse)
async def add_stock_item(
    request: Request,
    name: str = Form(...),
    category_id: str | None = Form(None),
    status: StockStatus = Form(StockStatus.normal),
    db: Session = Depends(get_db),
):
    if error := name_conflict(request, db, name):
        return error
    db.add(Item(name=name, category_id=parse_category_id(category_id), status=status))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return duplicate_response(request, clean_name(name))
    return render_stock_list(request, db)


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
    return render_stock_list(request, db)


@router.delete("/stock/items/{item_id}", response_class=HTMLResponse)
async def delete_stock_item(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    deleted = None
    if item:
        deleted = {"name": item.name, "category_id": item.category_id or "", "status": item.status.value}
        db.delete(item)
        db.commit()
    response = render_stock_list(request, db)
    if deleted:
        t = get_t(request)
        response.headers["HX-Trigger"] = json.dumps({
            "item-deleted": {
                "message": t["toast_deleted"].format(name=deleted["name"]),
                "undo": t["btn_undo"],
                "item": deleted,
            }
        })
    return response


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
        if error := name_conflict(request, db, name, exclude_id=item.id):
            return error
        item.name = name
        item.category_id = parse_category_id(category_id)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return duplicate_response(request, clean_name(name))
    return render_stock_list(request, db)
