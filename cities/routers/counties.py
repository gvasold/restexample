from typing import List, Optional, Union

import sqlalchemy.exc
from fastapi import (APIRouter, Depends, HTTPException, Path, Query, Request,
                     Response)
from sqlalchemy.orm import Session

from .. import crud, database, models, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/counties",
    tags=["counties"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)


@router.options("/", status_code=204, response_class=Response)
async def options_countries(response: Response):
    "Options for /counties."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@router.head("/")
@router.get("/", response_model=List[schemas.County])
async def get_counties(
    request: Request,
    db: Session = Depends(get_db),
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
    country: Union[str, None] = Query(
        default=None,
        title="filter by country",
        description="Filter result by country name.",
    ),
):
    "Get an ordered list of counties."
    counties = []
    for db_county in crud.get_counties(
        db=db, skip=start - 1, limit=size, q=q, country=country
    ):
        counties.append(schemas.County.from_model(request, db_county))
    return counties



@router.post("/", response_model=schemas.CountyDetails, status_code=201)
async def create_county(
    request: Request, county: schemas.CountyCreate, db: Session = Depends(get_db)
):
    "Create a new County."
    db_county = crud.get_county_by_name(db, county.name)
    if db_county:
        raise HTTPException(status_code=400, detail="County already exists.")
    else:
        try:
            db_county = crud.create_county(db=db, county=county, county_id=county.id)
            return schemas.CountyDetails.from_model(request, db_county)
        except ((sqlalchemy.exc.IntegrityError, crud.CreationException)) as err:
            raise HTTPException(status_code=400, detail=f"{err}")


