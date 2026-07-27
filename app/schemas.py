"""Request and response schemas for the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerProfileCreate(BaseModel):
    """Data accepted when creating a customer profile."""

    external_id: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)


class CustomerProfileRead(BaseModel):
    """Customer profile data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    email: str | None
    first_name: str | None
    last_name: str | None
    created_at: datetime
