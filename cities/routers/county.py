"""Endpoints for /county/{county_id}.
"""

import sqlalchemy.exc
from fastapi import (APIRouter, Depends, HTTPException, Query, Request,
                     Response)
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/counties",
    tags=["county"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)

@router.head("/{county_id}")
@router.get(
    "/{county_id}",
    response_model=schemas.CountyDetails
)
async def get_county_by_id(
    request: Request,
    county_id: int = Query(
        default=..., title="County id", description="The id of the county to request."
    ),
    db: Session = Depends(get_db),
):
    "Get County with id `county_id`."
    db_county = crud.get_county(db=db, county_id=county_id)
    if not db_county:
        raise HTTPException(status_code=404, detail="County does not exist.")
    return schemas.CountyDetails.from_model(request, db_county)


@router.options("/{county_id}", status_code=204, response_class=Response)
async def options_counties_with_id(county_id: int, response: Response):
    "Options for /counties/{counties_id}"
    # pylint: disable=W0613
    response.headers["Allow"] = "GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response

@router.put(
    "/{county_id}",
    response_model=schemas.CountyDetails,
)
async def create_or_update_county(
    request: Request,
    response: Response,
    county_id: int,
    county: schemas.CountyCreate,
    db: Session = Depends(get_db),
):
    "Create a new or update an existing County."
    db_county = crud.get_county(db, county_id=county_id)
    try:
        if db_county:
            # `id` is ignored anyhow, but I think it's more clear to raise a 400
            if county.id and county.id != county_id:
                raise HTTPException(
                    status_code=400, detail="Changing the id of a County is not allowed"
                )
            try:
                db_county = crud.update_county(
                    db=db,
                    county_id=county_id,
                    county_name=county.name,
                    country_id=county.country_id,
                )
                response.status_code = 200
            except crud.UpdateException as err:
                raise HTTPException(status_code=400, detail=f"{err}") from err
        else:
            db_county = crud.create_county(db=db, county_id=county_id, county=county)
            response.status_code = 201
        return schemas.CountyDetails.from_model(request, db_county)
    except sqlalchemy.exc.IntegrityError as err:
        raise HTTPException(status_code=400, detail=f"{err}") from err


@router.patch(
    "/{county_id}",
    response_model=schemas.CountyDetails,
    #responses={404: {"model": schemas.Message}},
)
def patch_county(
    request: Request,
    county_id: int,
    county: schemas.CountyPatch,
    db: Session = Depends(get_db),
):
    """Patch a county.

    Updates the county with the provided values.
    """
    try:
        db_county = crud.update_county(
            db,
            county_id=county_id,
            county_name=county.name,
            country_id=county.country_id,
        )
        return schemas.CountyDetails.from_model(request, db_county)
    except crud.ItemNotFoundException as err:
        raise HTTPException(status_code=404, detail="No such County") from err
    except crud.UpdateException as err:
        raise HTTPException(status_code=422, detail=f"{err}") from err
