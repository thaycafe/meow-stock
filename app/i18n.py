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
        "placeholder_search": "Search pantry",
        "placeholder_list_add": "I need…",
        "label_no_category": "No category",
        "btn_add": "Add",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_delete": "Delete",
        "btn_undo": "Undo",
        "btn_add_stock_item": "Track item",
        "btn_put_on_list": "Add to list",
        "btn_finish_shopping": "Finish shopping",
        "status_normal": "In stock",
        "status_running_low": "Running low",
        "status_out_of_stock": "Out of stock",
        "stock_title": "Pantry",
        "stock_empty_title": "Your pantry is empty",
        "stock_empty_subtitle": "Tap “Track item” to add your first item",
        "stock_no_results": "No items match your search",
        "list_empty_title": "Nothing to buy!",
        "list_empty_subtitle": "Add something below or mark pantry items as running low",
        "list_cart_title": "In the cart",
        "list_all_in_cart": "Everything is in the cart",
        "toast_deleted": "“{name}” deleted",
        "error_duplicate_item": "“{name}” is already in your pantry",
        "error_already_on_list": "“{name}” is already on the list",
        "error_empty_name": "Item name can't be empty",
        "error_generic": "Something went wrong. Please try again.",
        "aria_dark_mode": "Dark mode",
        "aria_language": "Language",
        "aria_edit_item": "Edit",
        "aria_item_status": "Stock status",
        "aria_status_filter": "Filter by status",
        **{f"cat_{k}": v["en"] for k, v in CATEGORY_KEYS.items()},
    },
    "pt": {
        "app_title": "Meow Estoque",
        "nav_list": "Lista",
        "nav_stock": "Despensa",
        "filter_all": "Todos",
        "placeholder_item_name": "Nome do item",
        "placeholder_no_category": "Sem categoria",
        "placeholder_search": "Buscar na despensa",
        "placeholder_list_add": "Preciso de…",
        "label_no_category": "Sem categoria",
        "btn_add": "Adicionar",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
        "btn_delete": "Apagar",
        "btn_undo": "Desfazer",
        "btn_add_stock_item": "Adicionar item",
        "btn_put_on_list": "Colocar na lista",
        "btn_finish_shopping": "Concluir compras",
        "status_normal": "Em estoque",
        "status_running_low": "Acabando",
        "status_out_of_stock": "Acabou",
        "stock_title": "Despensa",
        "stock_empty_title": "Sua despensa está vazia",
        "stock_empty_subtitle": "Toque em “Adicionar item” para começar",
        "stock_no_results": "Nenhum item encontrado",
        "list_empty_title": "Nada para comprar!",
        "list_empty_subtitle": "Adicione algo abaixo ou marque itens da despensa como acabando",
        "list_cart_title": "No carrinho",
        "list_all_in_cart": "Está tudo no carrinho",
        "toast_deleted": "“{name}” apagado",
        "error_duplicate_item": "“{name}” já está na despensa",
        "error_already_on_list": "“{name}” já está na lista",
        "error_empty_name": "O nome do item não pode ficar vazio",
        "error_generic": "Algo deu errado. Tente novamente.",
        "aria_dark_mode": "Modo escuro",
        "aria_language": "Idioma",
        "aria_edit_item": "Editar",
        "aria_item_status": "Situação do estoque",
        "aria_status_filter": "Filtrar por situação",
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
