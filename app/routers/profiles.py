"""Customer profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CustomerProfile
from app.schemas import (
    CustomerProfileCreate,
    CustomerProfileRead,
    CustomerProfileUpdate,
)


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=CustomerProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: CustomerProfileCreate,
    db: Session = Depends(get_db),
) -> CustomerProfile:
    """Create a customer profile with a unique external identifier."""
    existing_profile = db.scalar(
        select(CustomerProfile).where(
            CustomerProfile.external_id == profile_data.external_id,
        ),
    )
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A profile with this external_id already exists.",
        )

    profile = CustomerProfile(**profile_data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{external_id}", response_model=CustomerProfileRead)
def get_profile(external_id: str, db: Session = Depends(get_db)) -> CustomerProfile:
    """Retrieve a customer profile by its external identifier."""
    profile = db.scalar(
        select(CustomerProfile).where(CustomerProfile.external_id == external_id),
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    return profile


@router.put("/{external_id}", response_model=CustomerProfileRead)
def update_profile(
    external_id: str,
    profile_data: CustomerProfileUpdate,
    db: Session = Depends(get_db),
) -> CustomerProfile:
    """Update the mutable attributes of an existing customer profile."""
    profile = db.scalar(
        select(CustomerProfile).where(CustomerProfile.external_id == external_id),
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    updates = profile_data.model_dump(exclude_unset=True)
    email = updates.get("email")
    if email is not None:
        existing_email_owner = db.scalar(
            select(CustomerProfile).where(CustomerProfile.email == email),
        )
        if existing_email_owner is not None and existing_email_owner.id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A profile with this email already exists.",
            )

    for attribute, value in updates.items():
        setattr(profile, attribute, value)
    db.commit()
    db.refresh(profile)
    return profile
