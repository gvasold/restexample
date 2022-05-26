"Schemas for incomming and outgoing data."

from typing import List, TypeVar, Union

from fastapi import Request
from pydantic import BaseModel, Field

from cities import models


class CountryBase(BaseModel):
    "Pydantic Base Model for Country."
    name: str = Field(description="Name of the country")


class CountryCreate(CountryBase):
    "Request body for creation of a Country."
    id: Union[int, None] = None


# needed for the from_model annotations.
Country_ = TypeVar("Country_", bound="Country")


class Country(CountryBase):
    "Minimal data about a country."
    id: int
    link: Union[str, None] = Field(description="Link to country details.")

    class Config:
        orm_mode = True

    @classmethod
    def from_model(
        cls: Country_, request: Request, db_country: models.Country
    ) -> Country_:
        "Create a Country object from database model object."
        return Country(
            id=db_country.id,
            name=db_country.name,
            link=request.url_for("get_country_by_id", country_id=db_country.id),
        )


class CountyBase(BaseModel):
    "Base Class of all County Schema Classes"
    name: str


# needed for the from_model annotations.
County_ = TypeVar("County_", bound="Country")


class County(CountyBase):
    "Schema class for minimal County Responses like in listings."
    id: int
    link: Union[str, None] = Field(description="Link to county details.")

    @classmethod
    def from_model(cls: County_, request: Request, db_county: models.County) -> County_:
        "Construct a County Schema Object from ORM data."
        return County(
            id=db_county.id,
            name=db_county.name,
            link=request.url_for("get_county_by_id", county_id=db_county.id),
        )


# needed for the from_model annotations.
CountryDetails_ = TypeVar("CountryDetails_", bound="CountryDetails")


class CountryDetails(CountryBase):
    "The Schema Class for detailed Country data in responses."
    id: int
    link: Union[str, None] = Field(description="Link to country details.")
    counties: List[County] = []

    @classmethod
    def from_model(
        cls: CountryDetails_, request: Request, db_country: models.Country
    ) -> CountryDetails_:
        "Return a CountryDetail Object constructed from a models.Country object."
        country = CountryDetails(
            id=db_country.id,
            name=db_country.name,
            link=request.url_for("get_country_by_id", country_id=db_country.id),
        )
        for county in db_country.counties:
            country.counties.append(County.from_model(request, county))
        return country


class CountyCreate(CountyBase):
    "Schema class for incoming County data."
    id: Union[int, None] = None
    name: str
    country_id: int


class CityBase(BaseModel):
    "Base class of all City schema classes."
    name: str


# needed for the from_model annotations.
City_ = TypeVar("City_", bound="City")


class City(CityBase):
    """Schema Class for compact City responses.

    This is mainly used for listings.
    """

    id: int
    link: Union[str, None] = Field(description="Link to city details.")

    class Config:
        orm_mode = True

    @classmethod
    def from_model(cls: City_, request: Request, db_city: models.City):
        "Create a schemas.City object from the ORM object."
        return City(
            id=db_city.id,
            name=db_city.name,
            population=db_city.population,
            link=request.url_for("get_city_by_id", city_id=db_city.id),
        )


# needed for the from_model annotations.
CountyDetails_ = TypeVar("CountyDetails_", bound="CountyDetails")


class CountyDetails(CountyBase):
    "Schema class for detailed City responses."
    id: int
    name: str
    link: Union[str, None] = Field(description="Link to county details.")
    country: Union[Country, None]
    cities: List[City] = []

    class Config:
        orm_mode = True

    @classmethod
    def from_model(
        cls: CountyDetails_, request: Request, db_county: models.County
    ) -> CountyDetails_:
        "Return a CountyDetail Object constructed from a models.County object."
        county = CountyDetails(
            id=db_county.id,
            name=db_county.name,
            link=request.url_for("get_county_by_id", county_id=db_county.id),
        )
        county.country = Country.from_model(request, db_county.country)
        for city in db_county.cities:
            county.cities.append(City.from_model(request, city))
        return county


class CityCreate(CityBase):
    "Schema class for incoming City data."
    id: Union[int, None] = None
    name: str
    population: int
    county_id: int


# needed for the from_model annotations.
CityDetails_ = TypeVar("CityDetails_", bound="CityDetails")


class CityDetails(CityBase):
    "Schema class for outgoing detailed City data."
    id: int
    population: int
    link: Union[str, None] = Field(description="Link to city details.")
    county: County
    country: Country

    class Config:
        orm_mode = True

    @classmethod
    def from_model(
        cls: CityDetails_, request: Request, db_city: models.City
    ) -> CityDetails_:
        "Return a CityDetail Object constructed from a models.City object."
        return CityDetails(
            id=db_city.id,
            name=db_city.name,
            population=db_city.population,
            link=request.url_for("get_city_by_id", city_id=db_city.id),
            county=County.from_model(request, db_city.county),
            country=Country.from_model(request, db_city.county.country),
        )
