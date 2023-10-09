from sqlalchemy import Column, Integer, Text, Float
from app.database import Base
from geoalchemy2 import Geometry



class Restaurant(Base):
    __tablename__ = "restaurant"

    id = Column(Text, primary_key=True, index=True) # -- UUID (Should be auto-generated)
    rating = Column(Integer, index=True)
    name = Column(Text)
    site = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    street = Column(Text)
    city = Column(Text)
    state = Column(Text)
    lat = Column(Float)
    lng = Column(Float)
    location = Column(Geometry(geometry_type='POINT', srid=4326))

