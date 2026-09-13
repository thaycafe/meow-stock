from fastapi import Request

CATEGORY_KEYS = {
    "produce":   {"pt": "Hortifruti",  "en": "Produce"},
    "dairy":     {"pt": "Laticínios",  "en": "Dairy"},
    "meat":      {"pt": "Carnes",      "en": "Meat"},
    "bakery":    {"pt": "Padaria",     "en": "Bakery"},
    "beverages": {"pt": "Bebidas",     "en": "Beverages"},
    "cleaning":  {"pt": "Limpeza",     "en": "Cleaning"},
    "other":     {"pt": "Outros",      "en": "Other"},
    "grocery":  {"pt": "Mercearia",   "en": "Grocery"},
    "canned":   {"pt": "Conservas",   "en": "Canned Goods"},
}

TRANSLATIONS = {
    "en": {
        "app_title": "Meow Stock",
        "nav_list": "List",
        "nav_stock": "Pantry",
        "filter_all": "All",
        "placeholder_item_name": "Item name",
        "placeholder_no_category": "No category",
        "label_no_category": "Other",
        "btn_add": "Add",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_bought": "Bought",
        "btn_add_stock_item": "Track item",
        "status_normal": "In stock",
        "status_running_low": "Running low",
        "status_out_of_stock": "Out of stock",
        "stock_title": "Pantry",
        "stock_empty_title": "All stocked up!",
        "stock_empty_subtitle": "Mark items as running low or out of stock",
        "stock_section_normal": "In Stock",
        "stock_section_running_low": "Running Low",
        "stock_section_out_of_stock": "Out of Stock",
        "list_empty_title": "Nothing to buy!",
        "list_empty_subtitle": "Mark pantry items as running low or out of stock",
        "list_section_out_of_stock": "Out of Stock",
        "list_section_running_low": "Running Low",
        **{f"cat_{k}": v["en"] for k, v in CATEGORY_KEYS.items()},
    },
    "pt": {
        "app_title": "Meow Estoque",
        "nav_list": "Lista",
        "nav_stock": "Despensa",
        "filter_all": "Todos",
        "placeholder_item_name": "Nome do item",
        "placeholder_no_category": "Sem categoria",
        "label_no_category": "Sem categoria",
        "btn_add": "Adicionar",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
        "btn_bought": "Comprei",
        "btn_add_stock_item": "Adicionar item",
        "status_normal": "Em estoque",
        "status_running_low": "Acabando",
        "status_out_of_stock": "Acabou",
        "stock_title": "Despensa",
        "stock_empty_title": "Tudo em estoque!",
        "stock_empty_subtitle": "Marque itens que estão acabando ou que acabaram",
        "stock_section_normal": "Em estoque",
        "stock_section_running_low": "Acabando",
        "stock_section_out_of_stock": "Acabou",
        "list_empty_title": "Nada para comprar!",
        "list_empty_subtitle": "Marque itens da despensa como acabando ou acabou",
        "list_section_out_of_stock": "Acabou",
        "list_section_running_low": "Acabando",
        **{f"cat_{k}": v["pt"] for k, v in CATEGORY_KEYS.items()},
    },
}

DEFAULT_LANG = "pt"
SUPPORTED_LANGS = list(TRANSLATIONS.keys())


def get_lang(request: Request) -> str:
    lang = request.session.get("lang", DEFAULT_LANG)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def get_t(request: Request) -> dict:
    return TRANSLATIONS[get_lang(request)]


def translate_category(category, lang: str) -> str:
    if category is None:
        return ""
    if category.key and category.key in CATEGORY_KEYS:
        return CATEGORY_KEYS[category.key].get(lang, category.name)
    return category.name
