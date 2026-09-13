import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.database import Base, engine, get_db
from app.i18n import get_lang, get_t, SUPPORTED_LANGS, translate_category
from app.models import Category, Item, StockStatus
from app.routers import items as items_router
from app.routers import stock as stock_router

Path("data").mkdir(exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY", "dev-secret"))
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(items_router.router)
app.include_router(stock_router.router)

templates = Jinja2Templates(directory="app/templates")


def seed_categories():
    db = next(get_db())
    if db.query(Category).count() == 0:
        defaults = [
            Category(name="Hortifruti",  key="produce",   color="green"),
            Category(name="Laticínios",  key="dairy",     color="yellow"),
            Category(name="Carnes",      key="meat",      color="red"),
            Category(name="Padaria",     key="bakery",    color="orange"),
            Category(name="Bebidas",     key="beverages", color="blue"),
            Category(name="Limpeza",     key="cleaning",  color="purple"),
            Category(name="Outros",      key="other",     color="slate"),
        ]
        db.add_all(defaults)
        db.commit()


seed_categories()


def ctx(request: Request, **extra) -> dict:
    lang = get_lang(request)
    return {"request": request, "t": get_t(request), "lang": lang,
            "translate_category": lambda cat: translate_category(cat, lang), **extra}


@app.post("/lang/{lang}")
async def set_language(request: Request, lang: str):
    if lang in SUPPORTED_LANGS:
        request.session["lang"] = lang
    return RedirectResponse(request.headers.get("referer", "/"), status_code=302)


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/list", status_code=302)


@app.get("/list", response_class=HTMLResponse)
async def list_page(request: Request):
    db = next(get_db())
    from app.routers.items import get_list_by_category
    categories_with_items = get_list_by_category(db)
    return templates.TemplateResponse(
        "index.html",
        ctx(request, categories_with_items=categories_with_items),
    )
