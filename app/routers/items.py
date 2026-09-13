from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.i18n import get_lang, get_t, translate_category
from app.models import Item, StockStatus

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ctx(request: Request, **extra) -> dict:
    lang = get_lang(request)
    return {"request": request, "t": get_t(request), "lang": lang,
            "translate_category": lambda cat: translate_category(cat, lang), **extra}


def get_list_by_category(db: Session):
    items = (
        db.query(Item)
        .filter(Item.status.in_([StockStatus.out_of_stock, StockStatus.running_low]))
        .order_by(Item.name)
        .all()
    )
    groups: dict = {}
    no_cat = []
    for item in items:
        if item.category_id:
            groups.setdefault(item.category_id, {"category": item.category, "entries": []})
            groups[item.category_id]["entries"].append(item)
        else:
            no_cat.append(item)
    result = list(groups.values())
    result.sort(key=lambda g: g["category"].name)
    if no_cat:
        result.append({"category": None, "entries": no_cat})
    return result


@router.patch("/items/{item_id}/bought", response_class=HTMLResponse)
async def mark_bought(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.status = StockStatus.normal
        db.commit()
    categories_with_items = get_list_by_category(db)
    return templates.TemplateResponse(
        "partials/shopping_list.html",
        ctx(request, categories_with_items=categories_with_items),
    )
