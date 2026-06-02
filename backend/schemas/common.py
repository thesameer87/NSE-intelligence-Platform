from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema for all Pydantic models in the platform."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimeStampedSchema(BaseSchema):
    """Schema containing timestamp fields."""

    created_at: datetime
    updated_at: datetime | None = None
