from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator
from uuid import UUID, uuid4
import re


class RestaurantBase(BaseModel):
    rating: Optional[int] = None
    name: Optional[str] = None
    site: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

    @field_validator("email")
    def lower_email(v):
        """
        Normalizes the input email to lowercase
        """
        v = v.lower()
        return v

    @field_validator("rating")
    def val_rating(v):
        """
        Validates the input rating to values between 0-4
        """
        if v < 0 or v > 4:
            raise ValueError("rating must be between 0 and 4")
        return v

    @field_validator("phone")
    def validate_numerics(cls, v):
        regex = re.compile(r"^[0-9]+$")
        if not re.fullmatch(regex, v):
            raise ValueError("phone must be only digits")
        return v


class RestaurantCreate(RestaurantBase):
    id: Optional[UUID] = Field(default_factory=uuid4) # Generate an uuid


class RestaurantUpdate(RestaurantBase):
    pass



class RestaurantInDB(BaseModel):
    id: UUID
    rating: int
    name: str
    site: str
    email: EmailStr
    phone: str
    street: str
    city: str
    state: str
    lat: float
    lng: float



class Restaurant(RestaurantInDB):
    pass
