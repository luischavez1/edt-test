from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app import models, schemas, crud
import pandas as pd
import re
import unidecode
from sqlalchemy import text, func


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_str(input_string:str, characters_to_remove: str | list) -> str:
    """
    :param input_string:
    :param characters_to_remove:
    :return: A string with the given characters removed and with no consecutive spaces
    """
    result_string = ''.join(char for char in input_string if char not in characters_to_remove)
    result_string_without_extra_spaces = re.sub(r'\s+', ' ', result_string)

    return result_string_without_extra_spaces

@app.post("/populate/")
def populate_database(
        db: Session = Depends(get_db),
        file_in: UploadFile = File(default=None),
):
    """
    Given a csv file, populates the database
    :param db:
    :param file_in: A .csv format file
    :return:
    """
    # Validate if file is submitted
    if file_in is None:
        raise HTTPException(status_code=400, detail="Please provide a .csv file")

    # Validate format type
    format_type = file_in.content_type
    if format_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read file
    try:
        df = pd.read_csv(file_in.file)
        file_in.file.close()

        # Process data #
        # Strip to all string fields
        df.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Normalize phone, email, name and site
        df["phone"] = df["phone"].apply(func=clean_str, args=(" .-",))
        df["email"] = df["email"].apply(lambda x: x.lower())
        df["name"] = df["name"].apply(func=clean_str, args=("-",))
        df["site"] = df["site"].apply(lambda x: clean_str(unidecode.unidecode(x), " "))

        # Insert data into database
        inserted = df.to_sql(name="restaurant", if_exists="append", index=False, con=engine)

        # set location
        stmt = f"UPDATE restaurant SET location = ST_MakePoint(lng, lat)"
        sql = text(stmt)
        db.execute(sql)
        db.commit()

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="An error occurred when trying to process data")

    return f"Inserted {inserted} records in database"


@app.get("/restaurants/statistics")
def get_restaurant_stats(latitude: float, longitude: float, radius: float, db: Session = Depends(get_db)):
    try:
        count = (
            db.query(func.count())
            .filter(func.ST_DWithin(models.Restaurant.location, func.ST_MakePoint(longitude, latitude), radius))
            .scalar()
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


@app.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    restaurant_id = str(restaurant.id)

    db_restaurant = crud.get_restaurant(db=db, restaurant_id=restaurant_id)
    if db_restaurant:
        raise HTTPException(status_code=400, detail="There's already a restaurant with the given id")

    created = crud.create_restaurant(db=db, restaurant=restaurant)
    stmt = f"UPDATE restaurant SET location = ST_MakePoint(lng, lat) where id = '{created.id}'"
    sql = text(stmt)
    db.execute(sql)
    db.commit()

    return created


@app.get("/restaurants/{restaurant_id}", response_model=schemas.RestaurantCreate)
def read_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant


@app.put("/restaurants/{restaurant_id}", response_model=schemas.Restaurant)
def update_restaurant(restaurant_id: str, restaurant_update: schemas.RestaurantUpdate, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    updated = crud.update_restaurant(
        db=db,
        db_restaurant=db_restaurant,
        restaurant_in=restaurant_update
    )

    return updated


@app.delete("/restaurants/{restaurant_id}", response_model=schemas.RestaurantCreate)
def read_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    deleted_restaurant = crud.delete_restaurant(db=db,id=restaurant_id)
    return deleted_restaurant



