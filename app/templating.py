from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.i18n import get_lang, get_t, translate_category
from app.services import count_on_list

templates = Jinja2Templates(directory="app/templates")

CATEGORY_STYLES = {
    "green":  {"dot": "bg-green-500",  "text": "text-green-700 dark:text-green-300"},
    "yellow": {"dot": "bg-yellow-400", "text": "text-yellow-700 dark:text-yellow-300"},
    "red":    {"dot": "bg-red-500",    "text": "text-red-700 dark:text-red-300"},
    "orange": {"dot": "bg-orange-500", "text": "text-orange-700 dark:text-orange-300"},
    "blue":   {"dot": "bg-blue-500",   "text": "text-blue-700 dark:text-blue-300"},
    "purple": {"dot": "bg-purple-500", "text": "text-purple-700 dark:text-purple-300"},
    "slate":  {"dot": "bg-slate-400",  "text": "text-slate-600 dark:text-slate-300"},
    "amber":  {"dot": "bg-amber-500",  "text": "text-amber-700 dark:text-amber-300"},
    "teal":   {"dot": "bg-teal-500",   "text": "text-teal-700 dark:text-teal-300"},
}
templates.env.globals["category_style"] = lambda cat: CATEGORY_STYLES.get(
    cat.color if cat else "slate", CATEGORY_STYLES["slate"]
)


def ctx(request: Request, db: Session, **extra) -> dict:
    lang = get_lang(request)
    return {
        "t": get_t(request),
        "lang": lang,
        "translate_category": lambda cat: translate_category(cat, lang),
        "list_count": count_on_list(db),
        "is_htmx": request.headers.get("HX-Request") == "true",
        **extra,
    }


def render(request: Request, db: Session, template: str, **extra):
    return templates.TemplateResponse(request, template, ctx(request, db, **extra))
