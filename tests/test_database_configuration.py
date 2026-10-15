from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import main


ORDER_DATA = {
    "customer_code": "SYNTHETIC-CONFIG-001",
    "bicycle_description": "Bicicleta de prueba",
    "reported_issue": "Ajuste de prueba",
}


def test_environment_selects_persistent_database(tmp_path: Path, monkeypatch):
    database_path = tmp_path / "configured.sqlite3"
    monkeypatch.setenv("BIKE_REPAIR_DATABASE_PATH", str(database_path))

    with TestClient(main.create_app()) as client:
        created = client.post("/repair-orders", json=ORDER_DATA)
        assert created.status_code == 201

    assert database_path.is_file()
    with TestClient(main.create_app()) as client:
        response = client.get("/repair-orders")
        assert response.status_code == 200
        assert response.json() == [created.json()]


def test_explicit_database_path_overrides_environment(tmp_path: Path, monkeypatch):
    environment_path = tmp_path / "unused.sqlite3"
    explicit_path = tmp_path / "explicit.sqlite3"
    monkeypatch.setenv("BIKE_REPAIR_DATABASE_PATH", str(environment_path))

    with TestClient(main.create_app(explicit_path)) as client:
        assert client.post("/repair-orders", json=ORDER_DATA).status_code == 201

    assert explicit_path.is_file()
    assert not environment_path.exists()


@pytest.mark.parametrize("environment_value", [None, ""])
def test_unset_or_empty_environment_uses_default_database(
    tmp_path: Path, monkeypatch, environment_value: str | None
):
    # Replace the default only in this test to avoid the developer's runtime data.
    default_path = tmp_path / "default.sqlite3"
    monkeypatch.setattr(main, "DEFAULT_DATABASE_PATH", default_path)
    if environment_value is None:
        monkeypatch.delenv("BIKE_REPAIR_DATABASE_PATH", raising=False)
    else:
        monkeypatch.setenv("BIKE_REPAIR_DATABASE_PATH", environment_value)

    with TestClient(main.create_app()) as client:
        assert client.post("/repair-orders", json=ORDER_DATA).status_code == 201

    assert default_path.is_file()
