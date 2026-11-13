import json

from app.database import SessionLocal
from app.models import Item, StockStatus

HTMX = {"HX-Request": "true"}


def statuses():
    db = SessionLocal()
    try:
        return {i.name: i.status for i in db.query(Item).all()}
    finally:
        db.close()


def item_id(name):
    db = SessionLocal()
    try:
        return db.query(Item).filter(Item.name == name).one().id
    finally:
        db.close()


def test_quick_add_from_list_marks_item_out_of_stock(client):
    response = client.post("/list/items", data={"name": "Arroz"})

    assert response.status_code == 200
    assert statuses() == {"Arroz": StockStatus.out_of_stock}
    assert "Arroz" in client.get("/list").text


def test_duplicate_of_stocked_item_offers_to_put_it_on_the_list(client):
    client.post("/stock/items", data={"name": "Arroz", "status": "normal"})

    response = client.post("/list/items", data={"name": "arroz"})

    assert response.status_code == 409
    assert response.headers["X-Existing-Item-Id"] == str(item_id("Arroz"))

    client.patch(f"/list/items/{item_id('Arroz')}/need")
    assert statuses() == {"Arroz": StockStatus.out_of_stock}


def test_duplicate_of_item_already_on_list_says_so(client):
    client.post("/list/items", data={"name": "Arroz"})

    response = client.post("/stock/items", data={"name": "ARROZ"})

    assert response.status_code == 409
    assert response.text == "“Arroz” já está na lista"
    assert "X-Existing-Item-Id" not in response.headers


def test_checkout_restocks_only_items_in_the_cart(client):
    for name in ("Arroz", "Feijão", "Café"):
        client.post("/list/items", data={"name": name})
    client.post("/stock/items", data={"name": "Leite", "status": "normal"})

    response = client.post("/list/checkout", data={"ids": [item_id("Arroz"), item_id("Café")]})

    assert response.status_code == 200
    assert statuses() == {
        "Arroz": StockStatus.normal,
        "Feijão": StockStatus.out_of_stock,
        "Café": StockStatus.normal,
        "Leite": StockStatus.normal,
    }


def test_delete_returns_item_data_for_undo(client):
    client.post("/stock/items", data={"name": "Feijão", "status": "running_low", "category_id": "1"})

    response = client.delete(f"/stock/items/{item_id('Feijão')}")

    event = json.loads(response.headers["HX-Trigger"])["item-deleted"]
    assert event["message"] == "“Feijão” apagado"
    assert event["item"] == {"name": "Feijão", "category_id": 1, "status": "running_low"}
    assert statuses() == {}

    client.post("/stock/items", data=event["item"])
    assert statuses() == {"Feijão": StockStatus.running_low}


def test_ids_of_deleted_items_are_not_reused(client):
    client.post("/stock/items", data={"name": "Arroz"})
    client.post("/stock/items", data={"name": "Feijão"})
    deleted_id = item_id("Feijão")
    client.delete(f"/stock/items/{deleted_id}")

    client.post("/stock/items", data={"name": "Café"})

    assert item_id("Café") > deleted_id


def test_htmx_responses_refresh_the_list_count_badge(client):
    client.post("/list/items", data={"name": "Arroz"})

    response = client.post("/list/items", data={"name": "Café"}, headers=HTMX)

    assert 'id="list-count" hx-swap-oob="true"' in response.text
    assert ">2</span>" in response.text
    assert 'hx-swap-oob' not in client.get("/list").text
