"""The entypoint of the app.
"""
from fastapi import FastAPI

from . import database, models
from .routers import cities, city, counties, countries, country, county

models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()
app.include_router(countries.router)
app.include_router(country.router)
app.include_router(counties.router)
app.include_router(county.router)
app.include_router(cities.router)
app.include_router(city.router)
