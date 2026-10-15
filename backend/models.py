from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RepairStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RepairOrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    customer_code: str = Field(min_length=1, max_length=40)
    bicycle_description: str = Field(min_length=1, max_length=200)
    reported_issue: str = Field(min_length=1, max_length=500)


class RepairOrder(RepairOrderCreate):
    id: int
    status: RepairStatus


class RepairOrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: RepairStatus

    @field_validator("status", mode="before")
    @classmethod
    def trim_status(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value
