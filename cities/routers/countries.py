from typing import List, Optional, Union

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy.orm import Session

from .. import crud, database, models, schemas
from ..dependencies import get_db

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
@router.get("/", response_model=List[schemas.Country])
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


@router.head(
    "/{country_id}",
)
@router.get(
    "/{country_id}",
    response_model=schemas.CountryDetails,
)
async def get_country_by_id(
    request: Request,
    db: Session = Depends(get_db),
    country_id: int = Path(
        default=..., title="Country id", description="The id of the country to request."
    ),
):
    "Get a single Country with id `country_id`."
    db_country = crud.get_country(db=db, country_id=country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country does not exist.")
    else:
        country = schemas.CountryDetails.from_model(request, db_country)
    return country


@router.options("/{country_id}", status_code=204, response_class=Response)
async def options_countries_with_id(country_id: int, response: Response):
    "Options for /countries/{country_id}."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response


@router.post("/", response_model=schemas.CountryDetails, status_code=201)
async def create_country(
    request: Request, country: schemas.CountryCreate, db: Session = Depends(get_db)
):
    "Create a new Country."
    db_country = crud.get_country_by_name(db, country.name)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already exists.")
    else:
        try:
            db_country = crud.create_country(
                db=db, country=country, country_id=country.id
            )
            return schemas.CountryDetails.from_model(request, db_country)
        except (sqlalchemy.exc.IntegrityError, crud.CreationException):
            raise HTTPException(
                status_code=400,
                detail=f"Country with id '{country.id}' already exists.",
            )


@router.put(
    "/{country_id}",
    response_model=schemas.CountryDetails,
)
async def create_or_update_country(
    response: Response,
    request: Request,
    country_id: int,
    country: schemas.CountryCreate,
    db: Session = Depends(get_db),
):
    "Create a new or update an existing country."
    db_country = crud.get_country(db, country_id=country_id)
    if db_country:
        # `id` is ignored anyhow, but I think it's more clear to raise a 400
        if country.id and country.id != country_id:
            raise HTTPException(
                status_code=400, detail="Changing the id of a Country is not allowed"
            )
        db_country = crud.update_country(
            db=db, country_id=country_id, country_name=country.name
        )
        response.status_code = 200
    else:
        db_country = crud.create_country(db=db, country_id=country_id, country=country)
        response.status_code = 201
    return schemas.CountryDetails.from_model(request, db_country)


@router.patch(
    "/{country_id}",
    response_model=schemas.CountryDetails,
)
def patch_country(
    request: Request,
    country_id: int,
    country: schemas.CountryPatch,
    db: Session = Depends(get_db),
):
    """Patch a country.

    Updates the country with the provided value.
    """
    try:
        db_country = crud.update_country(
            db,
            country_id=country_id,
            country_name=country.name,
        )
        return schemas.CountryDetails.from_model(request, db_country)
    except crud.ItemNotFoundException as err:
        raise HTTPException(status_code=404, detail="No such County")