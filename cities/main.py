from re import I
from typing import Optional, List, Dict
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## ---- countries -----


@app.head("/countries")
@app.get("/countries", response_model=List[schemas.Country])
async def get_countries(
    request: Request,
    db: Session = Depends(get_db),
    start: Optional[int] = 0,
    size: Optional[int] = 20,
    q: Optional[str] = None,
):
    "Get an ordered list of countries."
    countries = []
    for country in crud.get_countries(db=db, skip=start, limit=size, q=q):
        country.link = request.url_for("get_country_by_id", country_id=country.id)
        countries.append(country)
    return countries


@app.head("/countries/{country_id}")
@app.get("/countries/{country_id}", response_model=schemas.CountryDetails)
def get_country_by_id(request: Request, country_id: int, db: Session = Depends(get_db)):
    "Get a single Country with id `country_id`."
    db_country = crud.get_country(db=db, country_id=country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country does not exist.")
    else:
        country = schemas.CountryDetails(id=db_country.id, name=db_country.name)
        for county in db_country.counties:
            country.counties.append(
                schemas.County(
                    id=county.id,
                    name=county.name,
                    country_id=county.country_id,
                    link=request.url_for("get_county_by_id", county_id=county.id),
                )
            )
    return country


# TODO: Which Exeptions must be handled? eg sqlalchemy.exc.IntegrityError for recycled ids?
@app.post("/countries", response_model=schemas.Country, status_code=201)
def create_country(country: schemas.CountryCreate, db: Session = Depends(get_db)):
    "Create a new Country."
    db_country = crud.get_country_by_name(db, country.name)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already exists.")
    else:
        return crud.create_country(db=db, country=country, country_id=country.id)



@app.put("/countries/{country_id}", response_model=schemas.Country)
def create_or_update_country(
    country_id: int, country: schemas.CountryCreate, db: Session = Depends(get_db)
):
    "Create a new or update an existing country."
    db_country = crud.get_country(db, country_id=country_id)
    if db_country:
        return crud.update_country(db=db, country_id=country_id, country=country)
    else:
        return crud.create_country(db=db, country_id=country_id, country=country)


## ----- counties ------


@app.head("/counties")
@app.get("/counties", response_model=List[schemas.County])
async def get_counties(
    request: Request,
    db: Session = Depends(get_db),
    start: Optional[int] = 0,
    size: Optional[int] = 20,
    q: Optional[str] = None,
    country: Optional[str] = None,
):
    "Get an ordered list of counties."
    counties = []
    for db_county in crud.get_counties(
        db=db, skip=start, limit=size, q=q, country=country
    ):
        counties.append(
            schemas.County(
                id=db_county.id,
                name=db_county.name,
                country_id=db_county.country_id,
                link=request.url_for("get_county_by_id", county_id=db_county.id),
            )
        )
    return counties


@app.head("/counties/{county_id}")
@app.get("/counties/{county_id}")
def get_county_by_id(request: Request, county_id: int, db: Session = Depends(get_db)):
    "Get County with id `county_id`."
    db_county = crud.get_county(db=db, county_id=county_id)
    if not db_county:
        raise HTTPException(status_code=404, detail="County does not exist.")
    country = schemas.Country(
        id=db_county.country.id,
        name=db_county.country.name,
        link=request.url_for("get_country_by_id", country_id=db_county.country_id),
    )
    county = schemas.CountyDetails(
        id=db_county.id, name=db_county.name, country=country
    )
    for db_city in db_county.cities:
        county.cities.append(
            schemas.City(
                id=db_city.id,
                name=db_city.name,
                link=request.url_for("get_city_by_id", city_id=db_city.id),
                county_id=db_city.county_id,
            )
        )
    return county


@app.post("/counties", response_model=schemas.County)
def create_county(county: schemas.CountyCreate, db: Session = Depends(get_db)):
    "Create a new County."
    db_county = crud.get_county_by_name(db, county.name)
    if db_county:
        raise HTTPException(status_code=400, detail="County already exists.")
    else:
        return crud.create_county(db=db, county=county)


@app.put("/counties/{county_id}", response_model=schemas.County)
def create_or_update_county(
    county_id: int, county: schemas.CountyCreate, db: Session = Depends(get_db)
):
    "Create a new or update an existing County."
    db_county = crud.get_county(db, county_id=county_id)
    if db_county:
        db_county = crud.update_county(db=db, county_id=county_id, county=county)
    else:
        db_county = crud.create_county(db=db, county_id=county_id, county=county)
    return schemas.County(
        id=db_county.id, name=db_county.name, country_id=db_county.country_id
    )


## ----- Cities -----


@app.head("/cities")
@app.get("/cities", response_model=List[schemas.City])
async def get_cities(
    request: Request,
    start: Optional[int] = 0,
    size: Optional[int] = 20,
    q: Optional[str] = None,
    minpop: Optional[int] = None,
    maxpop: Optional[int] = None,
    county: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
):
    "Get an ordered list of cities."
    cities = []
    for db_city in crud.get_cities(
        db=db,
        skip=start,
        limit=size,
        q=q,
        minpop=minpop,
        maxpop=maxpop,
        county=county,
        country=country,
    ):
        cities.append(
            schemas.City(
                id=db_city.id,
                name=db_city.name,
                population=db_city.population,
                county_id=db_city.county_id,
                link=request.url_for("get_city_by_id", city_id=db_city.id),
            )
        )
    return cities


@app.head("/cities/{city_id}")
@app.get("/cities/{city_id}", response_model=schemas.CityDetails)
def get_city_by_id(request: Request, city_id: int, db: Session = Depends(get_db)):
    "Get City with id `city_id`."
    db_city = crud.get_city(db=db, city_id=city_id)
    if not db_city:
        raise HTTPException(status_code=404, detail="City does not exist.")
    return schemas.CityDetails(
        id=db_city.id,
        name=db_city.name,
        population=db_city.population,
        county=schemas.County(
            id=db_city.county.id,
            name=db_city.county.name,
            link=request.url_for('get_county_by_id', county_id=db_city.county.id)
            ),
        country = schemas.Country(
            id=db_city.county.country.id,
            name=db_city.county.country.name,
            link=request.url_for("get_country_by_id", country_id=db_city.county.country.id)
        )
    )
    


@app.post("/cities", response_model=schemas.City)
def create_city(city: schemas.CityCreate, db: Session = Depends(get_db)):
    "Create a new City."
    db_city = crud.get_city_by_name(db, city.name)
    if db_city:
        raise HTTPException(status_code=400, detail="City already exists.")
    else:
        return crud.create_city(db=db, city=city)


@app.put("/cities/{city_id}", response_model=schemas.City)
def create_or_update_city(
    city_id: int, city: schemas.CityCreate, db: Session = Depends(get_db)
):
    "Create a new or update an existing City."
    db_city = crud.get_city(db, city_id=city_id)
    if db_city:
        return crud.update_city(db=db, city_id=city_id, city=city)
    else:
        return crud.create_city(db=db, city=city)


@app.delete("/cities/{city_id}", response_model=schemas.City)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    "Delete a City."
    db_city = crud.delete_city(db, city_id)
    if db_city:
        return db_city
    else:
        raise HTTPException(status_code=404, detail="City not found.")
