import pytest

from app.database import SessionLocal
from app.models import Item


def add(client, name, status="normal"):
    return client.post("/stock/items", data={"name": name, "status": status})


@pytest.mark.parametrize("duplicate", ["Feijão", "feijao", "  FEIJÃO  ", "feijão"])
def test_add_rejects_duplicate_names(client, item_names, duplicate):
    assert add(client, "Feijão").status_code == 200

    response = add(client, duplicate)

    assert response.status_code == 409
    assert "Feijão" in response.text
    assert item_names() == ["Feijão"]


def test_add_rejects_blank_name(client, item_names):
    response = add(client, "   ")

    assert response.status_code == 422
    assert item_names() == []


def test_add_collapses_inner_whitespace(client, item_names):
    add(client, "  Arroz   Branco ")

    assert item_names() == ["Arroz Branco"]
    assert add(client, "arroz branco").status_code == 409


def test_edit_rejects_renaming_onto_another_item(client, item_names):
    add(client, "Arroz")
    add(client, "Feijão")
    db = SessionLocal()
    feijao_id = db.query(Item).filter(Item.name == "Feijão").one().id
    db.close()

    response = client.post(f"/stock/items/{feijao_id}/edit", data={"name": "ARROZ"})

    assert response.status_code == 409
    assert item_names() == ["Arroz", "Feijão"]


def test_edit_allows_changing_case_of_own_name(client, item_names):
    add(client, "arroz")
    db = SessionLocal()
    item_id = db.query(Item).one().id
    db.close()

    response = client.post(f"/stock/items/{item_id}/edit", data={"name": "Arroz"})

    assert response.status_code == 200
    assert item_names() == ["Arroz"]
