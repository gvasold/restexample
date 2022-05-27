from re import I
from typing import Optional, List, Dict, Union
from fastapi import Depends, Query, Path, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
import sqlalchemy.exc
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    "Function used for dependency injection of db connection."
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## ---- countries -----


@app.options("/countries", status_code=204, response_class=Response)
async def options_countries(response: Response):
    "Options for `/countries`."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@app.head("/countries")
@app.get("/countries", response_model=List[schemas.Country])
async def get_countries(
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


@app.head("/countries/{country_id}", responses={404: {"model": schemas.Message}})
@app.get(
    "/countries/{country_id}",
    response_model=schemas.CountryDetails,
    responses={404: {"model": schemas.Message}},
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


@app.options("/countries/{country_id}", status_code=204, response_class=Response)
async def options_countries_with_id(country_id: int, response: Response):
    "Options for /countries/{country_id}."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response


@app.post("/countries", response_model=schemas.CountryDetails, status_code=201)
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


@app.put(
    "/countries/{country_id}",
    response_model=schemas.CountryDetails,
    responses={
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
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
        db_country = crud.update_country(db=db, country_id=country_id, country_name=country.name)
        response.status_code = 200
    else:
        db_country = crud.create_country(db=db, country_id=country_id, country=country)
        response.status_code = 201
    return schemas.CountryDetails.from_model(request, db_country)


@app.patch(
    "/countries/{country_id}",
    response_model=schemas.CountryDetails,
    responses={404: {"model": schemas.Message}},
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


## ----- counties ------


@app.options("/counties", status_code=204, response_class=Response)
async def options_countries(response: Response):
    "Options for /counties."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@app.head("/counties")
@app.get("/counties", response_model=List[schemas.County])
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


@app.head("/counties/{county_id}", responses={404: {"model": schemas.Message}})
@app.get(
    "/counties/{county_id}",
    response_model=schemas.CountyDetails,
    responses={404: {"model": schemas.Message}},
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


@app.options("/counties/{county_id}", status_code=204, response_class=Response)
async def options_counties_with_id(county_id: int, response: Response):
    "Options for /counties/{counties_id}"
    response.headers["Allow"] = "GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response


@app.post("/counties", response_model=schemas.CountyDetails, status_code=201)
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


@app.put(
    "/counties/{county_id}",
    response_model=schemas.CountyDetails,
    responses={
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
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
                raise HTTPException(status_code=400, detail=f"{err}")
        else:
            db_county = crud.create_county(db=db, county_id=county_id, county=county)
            response.status_code = 201
        return schemas.CountyDetails.from_model(request, db_county)
    except sqlalchemy.exc.IntegrityError as err:
        raise HTTPException(status_code=400, detail=f"{err}")


@app.patch(
    "/counties/{county_id}",
    response_model=schemas.CountyDetails,
    responses={404: {"model": schemas.Message}},
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
        raise HTTPException(status_code=404, detail="No such County")
    except crud.UpdateException as err:
        raise HTTPException(status_code=422, detail=f"{err}")


## ----- Cities -----


@app.options("/cities", status_code=204, response_class=Response)
async def options_cities(response: Response):
    "Options for /cities."
    response.headers["Allow"] = "GET, HEAD, OPTIONS, POST"
    response.status_code = 204
    return response


@app.head("/cities")
@app.get("/cities", response_model=List[schemas.City])
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


@app.head("/cities/{city_id}", responses={404: {"model": schemas.Message}})
@app.get(
    "/cities/{city_id}",
    response_model=schemas.CityDetails,
    responses={404: {"model": schemas.Message}},
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


@app.post("/cities", response_model=schemas.CityDetails, status_code=201)
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


@app.put(
    "/cities/{city_id}",
    response_model=schemas.CityDetails,
    responses={
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
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


@app.patch(
    "/cities/{city_id}",
    response_model=schemas.CityDetails,
    responses={404: {"model": schemas.Message}},
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


@app.delete("/cities/{city_id}", response_model=schemas.CityDetails)
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


@app.options("/cities/{city_id}", status_code=204, response_class=Response)
async def options_cities_with_id(city_id: int, response: Response):
    "Options for /cities/{city_id}"
    response.headers["Allow"] = "DELETE, GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response
