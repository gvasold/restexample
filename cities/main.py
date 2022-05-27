from re import I
from typing import Optional, List, Dict, Union
from fastapi import Depends, Query, Path, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
import sqlalchemy.exc
from . import crud, models, schemas, database

from . dependencies import get_db
from .routers import countries, counties, cities
models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()
app.include_router(countries.router)
app.include_router(counties.router)
app.include_router(cities.router)
