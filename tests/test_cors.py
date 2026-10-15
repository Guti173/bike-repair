from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    with TestClient(create_app(tmp_path / "cors.sqlite3")) as test_client:
        yield test_client


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_allowed_origins_can_read_orders(client: TestClient, origin: str):
    response = client.get("/repair-orders", headers={"Origin": origin})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "access-control-allow-credentials" not in response.headers


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
@pytest.mark.parametrize("method", ["GET", "POST", "PATCH"])
def test_allowed_preflight(client: TestClient, origin: str, method: str):
    response = client.options(
        "/repair-orders/1/status" if method == "PATCH" else "/repair-orders",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert set(response.headers["access-control-allow-methods"].split(", ")) == {
        "GET", "POST", "PATCH"
    }
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


@pytest.mark.parametrize(
    "origin", ["http://localhost:5174", "https://localhost:5173", "http://127.0.0.1:8000", "null"]
)
def test_other_origins_are_not_allowed(client: TestClient, origin: str):
    response = client.get("/repair-orders", headers={"Origin": origin})
    preflight = client.options(
        "/repair-orders",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers


@pytest.mark.parametrize(
    "method,header", [("DELETE", "Content-Type"), ("POST", "X-Unexpected")]
)
def test_unneeded_methods_and_headers_are_rejected(
    client: TestClient, method: str, header: str
):
    response = client.options(
        "/repair-orders",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": header,
        },
    )

    assert response.status_code == 400
