from typing import Optional, List, Dict, Union

from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    "Pydantic Base Model for Country."
    name: str = Field(description="Name of the country")


class CountryCreate(CountryBase):
    "Request body for creation of a Country."
    id: Union[int, None] = None
    # pass


class Country(CountryBase):
    "Minimal data about a country."
    id: int
    link: Union[str, None] = Field(description="Link to country details.")

    class Config:
        orm_mode = True


class CountyBase(BaseModel):
    name: str


class County(CountyBase):
    id: int
    # name: str
    #    country_id: Union[int, None]
    link: Union[str, None] = Field(description="Link to county details.")


class CountryDetails(CountryBase):
    id: int
    link: Union[str, None] = Field(description="Link to country details.")
    counties: List[County] = []


class CountyCreate(CountyBase):
    id: Union[int, None] = None
    name: str
    country_id: int


class CityBase(BaseModel):
    name: str


#    population: int
#    county_id: int


class City(CityBase):
    id: int
    link: Union[str, None] = Field(description="Link to city details.")

    class Config:
        orm_mode = True


class CountyDetails(CountyBase):
    id: int
    name: str
    link: Union[str, None] = Field(description="Link to county details.")
    country: Union[Country, None]
    cities: List[City] = []

    class Config:
        orm_mode = True


class CityCreate(CityBase):
    id: Union[int, None] = None
    name: str
    population: int
    county_id: int


class CityDetails(CityBase):
    id: int
    population: int
    link: Union[str, None] = Field(description="Link to city details.")
    county: County
    country: Country

    class Config:
        orm_mode = True
