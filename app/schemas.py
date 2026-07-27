"""Request and response schemas for the API."""

from datetime import datetime
from typing import Any

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


class CustomerEventCreate(BaseModel):
    """Data accepted when recording a customer event."""

    event_type: str = Field(min_length=1, max_length=100)
    event_data: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None


class CustomerEventRead(BaseModel):
    """Customer event data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    event_type: str
    event_data: dict[str, Any]
    occurred_at: datetime
