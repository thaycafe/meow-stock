from fastapi import Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.i18n import get_t, translate_category
from app.models import Item, StockStatus, clean_name, name_key

LIST_STATUSES = (StockStatus.out_of_stock, StockStatus.running_low)
NO_CATEGORY = "none"


def count_on_list(db: Session) -> int:
    return db.query(Item).filter(Item.status.in_(LIST_STATUSES)).count()


def group_by_category(items: list[Item], lang: str) -> list[dict]:
    groups: dict = {}
    for item in items:
        groups.setdefault(item.category_id, {"category": item.category, "entries": []})["entries"].append(item)
    for group in groups.values():
        group["entries"].sort(key=lambda i: i.name_key)
        group["key"] = str(group["category"].id) if group["category"] else NO_CATEGORY
    return sorted(
        groups.values(),
        key=lambda g: (g["category"] is None, name_key(translate_category(g["category"], lang))),
    )


def name_conflict(request: Request, db: Session, name: str, exclude_id: int | None = None) -> PlainTextResponse | None:
    if not clean_name(name):
        return PlainTextResponse(get_t(request)["error_empty_name"], status_code=422)
    query = db.query(Item).filter(Item.name_key == name_key(name))
    if exclude_id is not None:
        query = query.filter(Item.id != exclude_id)
    existing = query.first()
    return duplicate_response(request, existing.name, existing) if existing else None


def duplicate_response(request: Request, name: str, existing: Item | None = None) -> PlainTextResponse:
    """409 response. When the existing item isn't on the shopping list yet, expose its id
    (X-Existing-Item-Id) so the UI can offer to put it on the list instead."""
    t = get_t(request)
    if existing is not None and existing.status in LIST_STATUSES:
        return PlainTextResponse(t["error_already_on_list"].format(name=name), status_code=409)
    headers = {"X-Existing-Item-Id": str(existing.id)} if existing is not None else None
    return PlainTextResponse(t["error_duplicate_item"].format(name=name), status_code=409, headers=headers)
