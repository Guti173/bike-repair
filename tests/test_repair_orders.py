from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app


FIELD_LIMITS = [
    ("customer_code", 40),
    ("bicycle_description", 200),
    ("reported_issue", 500),
]
REQUIRED_FIELDS = [field for field, _ in FIELD_LIMITS]
STATUSES = ["pending", "in_progress", "completed"]


@pytest.fixture
def order_data() -> dict[str, str]:
    return {
        "customer_code": "SYNTHETIC-001",
        "bicycle_description": "Bicicleta de prueba azul",
        "reported_issue": "Freno de prueba desajustado",
    }


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    return tmp_path / "test.sqlite3"


@pytest.fixture
def client(database_path: Path):
    with TestClient(create_app(database_path)) as test_client:
        yield test_client


def test_create_repair_order(client: TestClient, order_data: dict[str, str]):
    response = client.post("/repair-orders", json=order_data)

    assert response.status_code == 201
    order = response.json()
    assert type(order["id"]) is int
    assert order["id"] > 0
    assert order == {**order_data, "id": order["id"], "status": "pending"}


def test_ids_are_unique(client: TestClient, order_data: dict[str, str]):
    first = client.post("/repair-orders", json=order_data)
    second = client.post("/repair-orders", json=order_data)

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


def test_list_empty_database(client: TestClient):
    response = client.get("/repair-orders")

    assert response.status_code == 200
    assert response.json() == []


def test_list_repair_orders(client: TestClient, order_data: dict[str, str]):
    first = client.post("/repair-orders", json=order_data)
    second = client.post(
        "/repair-orders", json={**order_data, "customer_code": "SYNTHETIC-002"}
    )
    assert first.status_code == second.status_code == 201

    response = client.get("/repair-orders")

    assert response.status_code == 200
    assert response.json() == [first.json(), second.json()]


def test_orders_and_status_persist_after_restart(
    database_path: Path, order_data: dict[str, str]
):
    with TestClient(create_app(database_path)) as client:
        created = client.post("/repair-orders", json=order_data)
        assert created.status_code == 201
        order_id = created.json()["id"]

    with TestClient(create_app(database_path)) as client:
        assert client.get("/repair-orders").json() == [created.json()]
        updated = client.patch(
            f"/repair-orders/{order_id}/status", json={"status": "completed"}
        )
        assert updated.status_code == 200

    with TestClient(create_app(database_path)) as client:
        response = client.get("/repair-orders")
        assert response.status_code == 200
        assert response.json() == [updated.json()]


@pytest.mark.parametrize("source_status", STATUSES)
@pytest.mark.parametrize("target_status", STATUSES)
def test_valid_status_changes(
    client: TestClient,
    order_data: dict[str, str],
    source_status: str,
    target_status: str,
):
    created = client.post("/repair-orders", json=order_data)
    assert created.status_code == 201
    order = created.json()
    url = f"/repair-orders/{order['id']}/status"
    assert client.patch(url, json={"status": source_status}).status_code == 200

    response = client.patch(url, json={"status": target_status})

    assert response.status_code == 200
    assert response.json() == {**order, "status": target_status}
    assert client.get("/repair-orders").json() == [response.json()]


@pytest.mark.parametrize(
    "invalid_status", ["cancelled", "PENDING", "", " \t\n ", None, 1, [], {}]
)
def test_invalid_status_is_rejected(
    client: TestClient, order_data: dict[str, str], invalid_status: object
):
    created = client.post("/repair-orders", json=order_data)
    assert created.status_code == 201
    order = created.json()

    response = client.patch(
        f"/repair-orders/{order['id']}/status", json={"status": invalid_status}
    )

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == [order]


@pytest.mark.parametrize("order_id", [999, 0, -1])
def test_nonexistent_order_returns_404(client: TestClient, order_id: int):
    response = client.patch(
        f"/repair-orders/{order_id}/status", json={"status": "in_progress"}
    )

    assert response.status_code == 404
    assert client.get("/repair-orders").json() == []


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
@pytest.mark.parametrize("value", ["", " ", "\t\n ", None, 123, [], {}])
def test_invalid_required_values_are_rejected(
    client: TestClient, order_data: dict[str, str], field: str, value: object
):
    response = client.post("/repair-orders", json={**order_data, field: value})

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == []


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_required_fields_are_rejected(
    client: TestClient, order_data: dict[str, str], field: str
):
    del order_data[field]

    response = client.post("/repair-orders", json=order_data)

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == []


@pytest.mark.parametrize("field,limit", FIELD_LIMITS)
@pytest.mark.parametrize("at_maximum", [False, True])
def test_field_boundaries_are_accepted_after_trimming(
    client: TestClient,
    order_data: dict[str, str],
    field: str,
    limit: int,
    at_maximum: bool,
):
    value = "x" * (limit if at_maximum else 1)
    response = client.post(
        "/repair-orders", json={**order_data, field: f" \t{value}\n "}
    )

    assert response.status_code == 201
    assert response.json()[field] == value
    assert client.get("/repair-orders").json() == [response.json()]


@pytest.mark.parametrize("field,limit", FIELD_LIMITS)
def test_overlong_fields_are_rejected(
    client: TestClient, order_data: dict[str, str], field: str, limit: int
):
    response = client.post(
        "/repair-orders", json={**order_data, field: "x" * (limit + 1)}
    )

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == []


@pytest.mark.parametrize(
    "extra", [{"unexpected": "value"}, {"id": 10}, {"status": "completed"}]
)
def test_unexpected_creation_fields_are_rejected(
    client: TestClient, order_data: dict[str, str], extra: dict[str, object]
):
    response = client.post("/repair-orders", json={**order_data, **extra})

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == []


def test_unexpected_status_fields_are_rejected(
    client: TestClient, order_data: dict[str, str]
):
    created = client.post("/repair-orders", json=order_data)
    assert created.status_code == 201
    order = created.json()

    response = client.patch(
        f"/repair-orders/{order['id']}/status",
        json={"status": "completed", "reported_issue": "Unexpected update"},
    )

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == [order]


def test_missing_status_is_rejected(client: TestClient, order_data: dict[str, str]):
    created = client.post("/repair-orders", json=order_data)
    assert created.status_code == 201
    order = created.json()

    response = client.patch(f"/repair-orders/{order['id']}/status", json={})

    assert response.status_code == 422
    assert client.get("/repair-orders").json() == [order]


def test_status_whitespace_is_trimmed(client: TestClient, order_data: dict[str, str]):
    created = client.post("/repair-orders", json=order_data)
    assert created.status_code == 201
    order = created.json()

    response = client.patch(
        f"/repair-orders/{order['id']}/status", json={"status": " \tin_progress\n "}
    )

    assert response.status_code == 200
    assert response.json() == {**order, "status": "in_progress"}


@pytest.mark.parametrize("order_id", ["abc", "1.5", str(2**63), str(-(2**63) - 1)])
def test_invalid_order_id_is_rejected(client: TestClient, order_id: str):
    response = client.patch(
        f"/repair-orders/{order_id}/status", json={"status": "completed"}
    )

    assert response.status_code == 422


def test_sql_like_text_is_stored_as_data(
    client: TestClient, order_data: dict[str, str]
):
    payload = {**order_data, "reported_issue": "Test '); DROP TABLE repair_orders; --"}
    created = client.post("/repair-orders", json=payload)

    assert created.status_code == 201
    assert created.json()["reported_issue"] == payload["reported_issue"]
    assert client.get("/repair-orders").json() == [created.json()]
