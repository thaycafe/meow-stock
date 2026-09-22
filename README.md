# Meow Stock

Self-hosted pantry and shopping list app. Tracks stock status of household items and auto-generates a shopping list from anything running low or out of stock.

## Stack

- **FastAPI** + Jinja2 — server-rendered HTML
- **htmx 2.x** — dynamic UI without a JS framework
- **Alpine.js 3.x** — client-side state (forms, dark mode toggle)
- **Tailwind CSS** (CDN) — styling, dark mode via `class` strategy
- **SQLite** + SQLAlchemy 2.x — persistence
- **Docker** + docker-compose

## Features

- **Stock** (`/stock`) — full pantry management: add, edit, delete items; set stock status (normal / running low / out of stock); filter by category
- **Shopping List** (`/list`) — auto-generated shopping list from items that are running low or out of stock, grouped by category
- Category system with i18n (PT/EN) and color coding
- Dark mode
- No authentication

## Project structure

```
.
├── app/
│   ├── main.py           # App entry point, /list route
│   ├── models.py         # SQLAlchemy models (Item, Category, StockStatus)
│   ├── database.py       # DB session setup
│   ├── i18n.py           # Translations (PT/EN) and category key mapping
│   ├── routers/
│   │   ├── items.py      # PATCH /items/{id}/bought (mark as purchased)
│   │   └── stock.py      # CRUD for /stock
│   └── templates/
│       ├── base.html
│       ├── index.html    # Lista view
│       ├── stock.html    # Despensa view
│       └── partials/     # htmx fragments
├── static/               # favicon and static assets
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
