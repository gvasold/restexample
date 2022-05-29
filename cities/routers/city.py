"""Endpointy for /cities/{id}
"""
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/cities",
    tags=["city"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)


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
                raise HTTPException(status_code=422, detail=f"{err}") from err
        else:
            db_city = crud.create_city(db=db, city_id=city_id, city=city)
            response.status_code = 201
        return schemas.CityDetails.from_model(request, db_city)
    except sqlalchemy.exc.IntegrityError as err:
        raise HTTPException(status_code=422, detail=f"{err}") from err


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
        raise HTTPException(status_code=404, detail="No such City") from err
    except crud.UpdateException as err:
        raise HTTPException(status_code=422, detail=f"{err}") from err


@router.delete("/{city_id}", response_model=schemas.CityDetails)
async def delete_city(request: Request, city_id: int, db: Session = Depends(get_db)):
    "Delete a City."
    db_city = crud.get_city(db, city_id=city_id)
    if not db_city:
        raise HTTPException(status_code=404, detail="City not found.")
    # We create the response before actually deleting because
    # we need the SQLAlchemy references to County (which is gone after deletion)
    response_data = schemas.CityDetails.from_model(request, db_city)
    response_data.link = None  # Nothing left to link to
    crud.delete_city(db, city_id)
    return response_data


@router.options("/{city_id}", status_code=204, response_class=Response)
async def options_cities_with_id(city_id: int, response: Response):
    "Options for /cities/{city_id}"
    # pylint: disable=W0613
    response.headers["Allow"] = "DELETE, GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response
