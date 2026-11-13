import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import Base, engine, get_db
from app.i18n import SUPPORTED_LANGS
from app.models import Category
from app.routers import items as items_router
from app.routers import stock as stock_router

Path("data").mkdir(exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY", "dev-secret"))
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(items_router.router)
app.include_router(stock_router.router)


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


@app.post("/lang/{lang}")
async def set_language(request: Request, lang: str):
    if lang in SUPPORTED_LANGS:
        request.session["lang"] = lang
    return RedirectResponse(request.headers.get("referer", "/"), status_code=302)


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/list", status_code=302)
