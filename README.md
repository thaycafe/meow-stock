# Meow Stock

Self-hosted pantry and shopping list app. Tracks stock status of household items and auto-generates a shopping list from anything running low or out of stock.

## Stack

- **FastAPI** + Jinja2 — server-rendered HTML
- **htmx 2.x** — dynamic UI without a JS framework
- **Alpine.js 3.x** — client-side state (forms, search/filter, shopping cart, toasts, dark mode)
- **Tailwind CSS** (CDN) — styling, dark mode via `class` strategy
- **SQLite** + SQLAlchemy 2.x — persistence
- **Docker** + docker-compose

## Features

- **Stock** (`/stock`) — full pantry management, grouped by category: add, edit and delete items (with undo); set stock status (in stock / running low / out of stock) with a one-tap selector; search by name (accent-insensitive) and filter by status
- **Shopping List** (`/list`) — auto-generated from items that are running low or out of stock, grouped by category. Tap items to move them to the cart while shopping (kept on the device), then "Finish shopping" restocks them. New items can be added straight from the list
- Adding an item that already exists offers to put the existing one on the shopping list instead
- Category system with i18n (PT/EN) and color coding
- Dark mode
- No authentication

## Project structure

```
.
├── app/
│   ├── main.py           # App entry point, language switch
│   ├── models.py         # SQLAlchemy models (Item, Category, StockStatus)
│   ├── database.py       # DB session setup
│   ├── i18n.py           # Translations (PT/EN) and category key mapping
│   ├── services.py       # Shared item queries, grouping and duplicate checks
│   ├── templating.py     # Jinja2 setup and shared template context
│   ├── routers/
│   │   ├── items.py      # /list: shopping list, quick add, checkout
│   │   └── stock.py      # /stock: pantry CRUD
│   └── templates/
│       ├── base.html     # Layout, header/tabs, toast and Alpine stores
│       ├── macros.html   # Shared template macros
│       ├── index.html    # Lista view
│       ├── stock.html    # Despensa view
│       └── partials/     # htmx fragments
├── static/               # favicon and static assets
├── tests/                # pytest suite
├── data/                 # SQLite DB (volume-mounted, not in image)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Running

```bash
cp .env.example .env  # set APP_SECRET_KEY
docker compose up -d
# app available at http://localhost:8000
```

> Code is baked into the Docker image — only `data/` is volume-mounted. After any code change, rebuild: `docker compose build && docker compose up -d`

### Local development

Requires Python 3.10+ (the Docker image uses 3.12). Run every command from the project root — the app resolves `data/`, `static/` and `app/templates/` relative to it.

```bash
# One-time setup
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # app + test dependencies
cp .env.example .env                            # then set APP_SECRET_KEY

# Run with auto-reload at http://localhost:8000
.venv/bin/uvicorn app.main:app --reload --env-file .env

# Run the tests (they use a temporary database, never data/lista.db)
.venv/bin/python -m pytest
```

The SQLite database is created at `data/lista.db` on first start, with the default categories.
