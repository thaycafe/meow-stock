from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.i18n import get_lang
from app.models import Item, StockStatus, clean_name
from app.services import LIST_STATUSES, duplicate_response, group_by_category, name_conflict
from app.templating import render

router = APIRouter()


def render_shopping_list(request: Request, db: Session, template: str = "partials/shopping_list.html"):
    items = db.query(Item).filter(Item.status.in_(LIST_STATUSES)).all()
    return render(
        request, db, template,
        groups=group_by_category(items, get_lang(request)),
        item_ids=[i.id for i in items],
    )


@router.get("/list", response_class=HTMLResponse)
async def list_page(request: Request, db: Session = Depends(get_db)):
    return render_shopping_list(request, db, "index.html")


@router.post("/list/items", response_class=HTMLResponse)
async def add_to_list(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    if error := name_conflict(request, db, name):
        return error
    db.add(Item(name=name, status=StockStatus.out_of_stock))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return duplicate_response(request, clean_name(name))
    return render_shopping_list(request, db)


@router.patch("/list/items/{item_id}/need", response_class=HTMLResponse)
async def put_on_list(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item and item.status not in LIST_STATUSES:
        item.status = StockStatus.out_of_stock
        db.commit()
    return render_shopping_list(request, db)


@router.post("/list/checkout", response_class=HTMLResponse)
async def checkout(request: Request, ids: list[int] = Form(default=[]), db: Session = Depends(get_db)):
    if ids:
        (
            db.query(Item)
            .filter(Item.id.in_(ids), Item.status.in_(LIST_STATUSES))
            .update({Item.status: StockStatus.normal}, synchronize_session=False)
        )
        db.commit()
    return render_shopping_list(request, db)
