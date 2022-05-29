"CRUD function for Country, County and City."
import sqlalchemy
from sqlalchemy.orm import Session
import sqlalchemy.exc

from . import schemas
from .models import Country, County, City


class CRUDException(Exception):
    "A generic CRUD exception."

class CreationException(CRUDException):
    "Excepetion raised when creation of entry fails."

class UpdateException(CRUDException):
    "Excepetion raised when update of entry fails."

class ItemNotFoundException(CRUDException):
    "Excepetion raised when object to update does not exist."


## ----- Countries


def get_country(db: Session, country_id: int):
    "Get Country by id."
    return db.query(Country).filter(Country.id == country_id).first()


def get_countries(db: Session, skip: int = 0, limit: int = 100, q=None):
    "Get list of Countries."
    conditions = []
    if q:
        conditions.append(Country.name.ilike(f"%{q}%"))
    return (
        db.query(Country)
        .filter(*conditions)
        .order_by(Country.name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_country_by_name(db: Session, country_name: str):
    "Get Country by name."
    return db.query(Country).filter(Country.name == country_name).first()


def create_country(db: Session, country: schemas.CountyCreate, country_id: int = None):
    """Add a new Country.

    if country_id is None, database will create the id automatcally.
    """
    # This is handled by the database anyhow, but we want a nicer error message
    # and avoid a warning from sqlalchemy
    if country_id and get_country(db, country_id):
        raise CreationException(f"A country with id '{country_id}' already exists.")
    db_country = Country(name=country.name, id=country_id)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country


def update_country(db: Session, country_id: int, country_name=None):
    """Update an existing Country."""
    db_country = get_country(db, country_id)
    if db_country:
        if country_name:
            db_country.name = country_name
            db.commit()
            db.refresh(db_country)
    else:
        raise ItemNotFoundException(f"Country with id {country_id} does not exist.")
    return db_country


## ------ Counties ----------------


def get_county(db: Session, county_id: int):
    "Get County by id."
    return db.query(County).filter(County.id == county_id).first()


def get_counties(db: Session, skip: int = 0, limit: int = 100, q=None, country=None):
    "Get a list of countries."
    conditions = []
    if q:
        conditions.append(County.name.ilike(f"%{q}%"))
    if country:
        conditions.append(Country.name == country)
    return (
        db.query(County)
        .join(Country)
        .filter(*conditions)
        .order_by(County.name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_county_by_name(db: Session, county_name: str):
    "Find County by county name."
    return db.query(County).filter(County.name == county_name).first()


def create_county(db: Session, county: schemas.CountyCreate, county_id=None):
    "Create a new county."
    # This is handled by the database anyhow, but we want a nicer error message
    # and avoid a warning from sqlalchemy
    if county_id and get_county(db, county_id):
        raise CreationException(f"A county with id '{county_id}' already exists.")
    db_county = County(id=county_id, name=county.name, country_id=county.country_id)
    db.add(db_county)
    db.commit()
    db.refresh(db_county)
    return db_county


def update_county(db: Session, county_id: int, county_name: str = None, country_id: int = None):
    "Create a new or update an exisisting County."
    db_county = get_county(db, county_id)
    if db_county:
        if county_name:
            db_county.name = county_name
        if country_id:
            db_county.country_id = country_id
        try:
            db.commit()
            db.refresh(db_county)
            return db_county
        except sqlalchemy.exc.IntegrityError as err:
            raise UpdateException(f"There is no country with id {country_id}.") from err
    else:
        raise ItemNotFoundException(f"County with id {county_id} does not exist.")


## ----- cities ----


def get_city(db: Session, city_id: int):
    "Get City by id."
    return db.query(City).filter(City.id == city_id).first()


def get_cities(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    q: str = None,
    minpop: int = None,
    maxpop: int = None,
    county: int = None,
    country: int = None,
):
    """Get a list of cities.

    Accepts a list of optional parameters:

    :param skip: Sets the offset
    :param limit: Sets the limit
    :param q: Filter cities by substring q searched in city.name
    :param minpop: Filter cities for a mininmal population
    :param maxpop: Filter cities for a maximal population
    :param county: Filter search for cities located in county
    :param country: Filter search for cities located in country
    """
    conditions = []
    if q:
        conditions.append(City.name.ilike(f"%{q}%"))
    if minpop:
        conditions.append(City.population >= minpop)
    if maxpop:
        conditions.append(City.population <= maxpop)
    if county:
        conditions.append(County.name == county)
    if country:
        conditions.append(Country.name == country)
    return (
        db.query(City)
        .join(County)
        .join(Country)
        .order_by(City.name)
        .filter(*conditions)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_city_by_name(db: Session, city_name: str):
    "Get City with name city_name."
    return db.query(City).filter(City.name == city_name).first()




def create_city(db: Session, city: schemas.CityCreate, city_id=None):
    "Create a new City. Id will be chosen by data base if None."
    # This is handled by the database anyhow, but we want a nicer error message
    # and avoid a warning from sqlalchemy
    if city_id and get_city(db, city_id):
        raise CreationException(f"A country with id '{city_id}' already exists.")
    db_city = City(
        name=city.name, population=city.population, county_id=city.county_id, id=city_id
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def update_city(
    db: Session,
    city_id: int,
    city_name: str = None,
    population: int = -1,  # we might want to set it to None
    county_id: int = None,
):
    "Update an existing City."
    db_city = get_city(db, city_id)
    if db_city:
        if city_name:
            db_city.name = city_name
        if population > -1:
            db_city.population = population
        if county_id:
            db_city.county_id = county_id
        try:
            db.commit()
            db.refresh(db_city)
            return db_city
        except sqlalchemy.exc.IntegrityError as err:
            raise UpdateException(f"There is no county with id {county_id}.") from err
    else:
        raise ItemNotFoundException(f"City with id {city_id} does not exist.")


def delete_city(db: Session, city_id: int):
    "Delete city with id city_id."
    db_city = get_city(db, city_id)
    if db_city:
        db.delete(db_city)
        db.commit()
    return db_city
