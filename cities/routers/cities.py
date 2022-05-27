from typing import List, Optional, Union

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy.orm import Session

from .. import crud, database, models, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/cities",
    tags=["counties"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)


@router.options("/", status_code=204, response_class=Response)
async def options_cities(response: Response):
    "Options for /cities."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@router.head("/")
@router.get("/", response_model=List[schemas.City])
async def get_cities(
    request: Request,
    start: Optional[int] = Query(
        default=1,
        gt=0,
        title="First result",
        description=(
            "Number of the first result entry to show. " "Can be used for paging."
        ),
    ),
    size: Optional[int] = Query(
        default=20,
        title="Number of result entries",
        gt=0,
        description="Number of counties to be returned. Can be used for paging.",
    ),
    q: Union[str, None] = Query(
        default=None, title="Query string", description="(Sub)String to search for."
    ),
    minpop: Union[int, None] = Query(
        default=None,
        gt=0,
        title="Minimum population",
        description=(
            "Set a minimum population filter. Filter for cities with a "
            "population greater equals `minpop`."
        ),
    ),
    maxpop: Union[int, None] = Query(
        default=None,
        gt=0,
        title="Maximum population",
        description=(
            "Set a maximum population filter. Filter for cities with a "
            "population less equals `maxpop`."
        ),
    ),
    county: Union[str, None] = Query(
        default=None,
        title="Filter by county",
        description="Filter cities by county name.",
    ),
    country: Union[str, None] = Query(
        default=None,
        title="Filter by country",
        description="Filter cities by country name.",
    ),
    db: Session = Depends(get_db),
):
    "Get an ordered list of cities."
    cities = []
    for db_city in crud.get_cities(
        db=db,
        skip=start - 1,
        limit=size,
        q=q,
        minpop=minpop,
        maxpop=maxpop,
        county=county,
        country=country,
    ):
        cities.append(schemas.City.from_model(request, db_city))
    return cities


@router.head("/{city_id}")
@router.get(
    "/{city_id}",
    response_model=schemas.CityDetails,
)
async def get_city_by_id(
    request: Request,
    city_id: int = Query(
        default=..., title="City id", description="The id of the city to request."
    ),
    db: Session = Depends(get_db),
):
    "Get City with id `city_id`."
    db_city = crud.get_city(db=db, city_id=city_id)
    if not db_city:
        raise HTTPException(status_code=404, detail="City does not exist.")
    return schemas.CityDetails.from_model(request, db_city)


@router.post(
    "/", response_model=schemas.CityDetails, status_code=201
)
async def create_city(
    request: Request, city: schemas.CityCreate, db: Session = Depends(get_db)
):
    "Create a new City."
    db_city = crud.get_city_by_name(db, city.name)
    if db_city:
        raise HTTPException(status_code=400, detail="City already exists.")
    else:
        try:
            db_city = crud.create_city(db=db, city=city, city_id=city.id)
            return schemas.CityDetails.from_model(request, db_city)
        except (sqlalchemy.exc.IntegrityError, crud.CreationException) as err:
            raise HTTPException(status_code=400, detail=f"{err}")


@router.put(
    "/{city_id}",
    response_model=schemas.CityDetails,
)
async def create_or_update_city(
    request: Request,
    response: Response,
    city_id: int,
    city: schemas.CityCreate,
    db: Session = Depends(get_db),
):
    "Create a new or update an existing City."
    db_city = crud.get_city(db, city_id=city_id)
    try:
        if db_city:
            if city.id and city.id != city_id:
                raise HTTPException(
                    status_code=422, detail="Changing the id of a City is not allowed"
                )
            try:
                db_city = crud.update_city(
                    db=db,
                    city_id=city_id,
                    city_name=city.name,
                    population=city.population,
                    county_id=city.county_id,
                )
                response.status_code = 200
            except crud.UpdateException as err:
                raise HTTPException(status_code=422, detail=f"{err}")
        else:
            db_city = crud.create_city(db=db, city_id=city_id, city=city)
            response.status_code = 201
        return schemas.CityDetails.from_model(request, db_city)
    except sqlalchemy.exc.IntegrityError as err:
        raise HTTPException(status_code=422, detail=f"{err}")


@router.patch(
    "/{city_id}",
    response_model=schemas.CityDetails,
)
def patch_city(
    request: Request,
    city_id: int,
    city: schemas.CityPatch,
    db: Session = Depends(get_db),
):
    """Patch a city.

    Updates the city with the provided values.
    """
    try:
        db_city = crud.update_city(
            db,
            city_id=city_id,
            city_name=city.name,
            population=city.population,
            county_id=city.county_id,
        )
        return schemas.CityDetails.from_model(request, db_city)
    except crud.ItemNotFoundException as err:
        raise HTTPException(status_code=404, detail="No such City")
    except crud.UpdateException as err:
        raise HTTPException(status_code=422, detail=f"{err}")


@router.delete("/{city_id}", response_model=schemas.CityDetails)
async def delete_city(request: Request, city_id: int, db: Session = Depends(get_db)):
    "Delete a City."
    db_city = crud.get_city(db, city_id=city_id)
    if db_city:
        # We create the response before actually deleting because
        # we need the SQLAlchemy references to County (which is gone after deletion)
        response_data = schemas.CityDetails.from_model(request, db_city)
        response_data.link = None  # Nothing left to link to
        crud.delete_city(db, city_id)
        return response_data
    else:
        raise HTTPException(status_code=404, detail="City not found.")


@router.options(
    "/{city_id}", status_code=204, response_class=Response
)
async def options_cities_with_id(city_id: int, response: Response):
    "Options for /cities/{city_id}"
    response.headers["Allow"] = "DELETE, GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response
