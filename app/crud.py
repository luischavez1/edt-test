from sqlalchemy.orm import Session
from typing import Union
from app import models, schemas

from fastapi.encoders import jsonable_encoder


def get_restaurant(db: Session, restaurant_id: str) -> models.Restaurant:
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()


def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate) -> models.Restaurant:
    restaurant_data = jsonable_encoder(restaurant)
    db_restaurant = models.Restaurant(**restaurant_data)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def update_restaurant(
        db: Session,
        db_restaurant: models.Restaurant,
        restaurant_in: Union[schemas.RestaurantUpdate]
) -> models.Restaurant:
    """Update a Restaurant Object"""
    restaurant_data = jsonable_encoder(db_restaurant)
    update_data = restaurant_in.model_dump(exclude_none=True)
    for field in restaurant_data:
        if field in update_data:
            setattr(db_restaurant, field, update_data[field])
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def delete_restaurant(db: Session, id: str) -> models.Restaurant:
    """Delete a Restaurant"""
    obj = db.query(models.Restaurant).get(id)
    db.delete(obj)
    db.commit()
    return obj
