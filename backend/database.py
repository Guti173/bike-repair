import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .models import RepairOrder, RepairOrderCreate, RepairStatus


@contextmanager
def _connection(database_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path) -> None:
    with _connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repair_orders (
                id INTEGER PRIMARY KEY,
                customer_code TEXT NOT NULL,
                bicycle_description TEXT NOT NULL,
                reported_issue TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'in_progress', 'completed'))
            )
            """
        )


def create_repair_order(
    database_path: Path, order: RepairOrderCreate
) -> RepairOrder:
    with _connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO repair_orders (
                customer_code, bicycle_description, reported_issue
            ) VALUES (?, ?, ?)
            """,
            (order.customer_code, order.bicycle_description, order.reported_issue),
        )
        row = connection.execute(
            "SELECT * FROM repair_orders WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return RepairOrder.model_validate(dict(row))


def list_repair_orders(database_path: Path) -> list[RepairOrder]:
    with _connection(database_path) as connection:
        rows = connection.execute(
            "SELECT * FROM repair_orders ORDER BY id"
        ).fetchall()
        return [RepairOrder.model_validate(dict(row)) for row in rows]


def update_repair_order_status(
    database_path: Path, order_id: int, status: RepairStatus
) -> RepairOrder | None:
    with _connection(database_path) as connection:
        cursor = connection.execute(
            "UPDATE repair_orders SET status = ? WHERE id = ?",
            (status.value, order_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            "SELECT * FROM repair_orders WHERE id = ?", (order_id,)
        ).fetchone()
        return RepairOrder.model_validate(dict(row))
