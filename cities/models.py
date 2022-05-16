from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    counties = relationship("County", back_populates="country")

class County(Base):
    __tablename__ = 'counties'    

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("Country", back_populates="counties")
    cities = relationship("City", back_populates="county")


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    population = Column(Integer)
    county_id = Column(Integer, ForeignKey("counties.id"))

    county = relationship("County", back_populates="cities")