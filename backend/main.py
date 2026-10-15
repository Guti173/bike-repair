from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path as PathParameter, status

from . import database
from .models import RepairOrder, RepairOrderCreate, RepairOrderStatusUpdate


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "repair_orders.sqlite3"


def create_app(database_path: str | Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    database_path = Path(database_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.initialize_database(database_path)
        yield

    app = FastAPI(title="Bike Repair Management", lifespan=lifespan)

    @app.post(
        "/repair-orders",
        response_model=RepairOrder,
        status_code=status.HTTP_201_CREATED,
    )
    def create_order(order: RepairOrderCreate) -> RepairOrder:
        return database.create_repair_order(database_path, order)

    @app.get("/repair-orders", response_model=list[RepairOrder])
    def list_orders() -> list[RepairOrder]:
        return database.list_repair_orders(database_path)

    @app.patch("/repair-orders/{id}/status", response_model=RepairOrder)
    def update_status(
        id: Annotated[int, PathParameter(ge=-(2**63), le=2**63 - 1)],
        update: RepairOrderStatusUpdate,
    ) -> RepairOrder:
        order = database.update_repair_order_status(database_path, id, update.status)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de reparación no encontrada.",
            )
        return order

    return app
