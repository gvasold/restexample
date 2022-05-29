"""Endpointy for /contries.
"""
from typing import Optional, Union

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from .. import crud, schemas
from .. dependencies import get_db

router = APIRouter(
    prefix="/countries",
    tags=["countries"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)

@router.options("/", status_code=204, response_class=Response)
async def options_countries(response: Response):
    "Options for `/countries`."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@router.head("/")
@router.get("/")#, response_model=List[schemas.Country])
async def get_countries(
    request: Request,
    db: Session = Depends(get_db),
    start: Optional[int] = Query(
        default=1,
        gt=0,
        title="First result",
        description="Number of the first result entry to show. Can be used for paging.",
    ),
    size: Optional[int] = Query(
        default=20,
        title="Number of result entries",
        gt=0,
        description="Number of countries to be returned. Can be used for paging.",
    ),
    q: Union[str, None] = Query(
        default=None, title="Query string", description="(Sub)String to search for."
    ),
):
    "Get an alphabetically ordered list of countries."
    countries = []
    for country in crud.get_countries(db=db, skip=start - 1, limit=size, q=q):
        countries.append(schemas.Country.from_model(request, country))
    return countries

@router.post("/", response_model=schemas.CountryDetails, status_code=201)
async def create_country(
    request: Request, country: schemas.CountryCreate, db: Session = Depends(get_db)
):
    "Create a new Country."
    db_country = crud.get_country_by_name(db, country.name)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already exists.")
    try:
        db_country = crud.create_country(
            db=db, country=country, country_id=country.id
        )
        return schemas.CountryDetails.from_model(request, db_country)
    except (sqlalchemy.exc.IntegrityError, crud.CreationException) as err:
        raise HTTPException(
            status_code=400,
            detail=f"Country with id '{country.id}' already exists.",
        ) from err
