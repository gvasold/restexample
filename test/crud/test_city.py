from re import I
from cities import crud
from cities.schemas import CityCreate
import pytest
import sqlalchemy.exc


def test_get_city(db, cities):
    "Test the get_city function."
    assert crud.get_city(db, 1).name == "City 1"
    assert crud.get_city(db, 99).name == "City 99"


def test_get_cities(db, cities):
    """Get all cities."""
    # Limit is 100 by default; we do not set a limit.
    result = crud.get_cities(db)
    assert len(result) == 100

    # Test if result is ordered by name
    assert result[0].id == 1
    assert result[1].id == 10
    assert result[2].id == 100

    # Set limit to 20
    result = crud.get_cities(db, limit=20)
    assert len(result) == 20
    assert result[0].id == 1

    # Set limit to 20 and skip 40
    result = crud.get_cities(db, skip=40, limit=20)
    assert len(result) == 20
    # because we sort by name and 5 later names slip in so the 41th entry has id 36
    assert result[0].id == 36


def test_get_cities_with_q(db, cities):
    "Get all cities containing value of q"
    result = crud.get_cities(db, q="ty 9")
    assert len(result) == 11  # 9 and 90 to 99
    assert result[0].name == "City 9"
    assert result[-1].name == "City 99"


def test_get_cities_with_minpop(db, cities):
    "Test the minpop param."
    result = crud.get_cities(db, minpop=1000)
    # population == id*10, 11 cities are >= 1000
    assert len(result) == 11
    assert result[0].id == 100


def test_get_cities_with_maxpop(db, cities):
    "Test the maxpop param."
    result = crud.get_cities(db, maxpop=100)
    assert len(result) == 10
    assert result[0].id == 1
    # City 10 come before City 2, so the last is 9
    assert result[-1].id == 9
    assert result[1].population == 100


def test_get_cities_with_pop_interval(db, cities):
    """As population=id*10, minpop=50, maxpop=90 should
    return Cities with ids 5, 6, 7, 8, 9.
    """
    result = crud.get_cities(db, minpop=50, maxpop=90)
    assert len(result) == 5
    assert result[0].id == 5
    assert result[-1].id == 9


def test_get_cities_with_county(db, cities):
    result = crud.get_cities(db, county="County 3")
    assert len(result) == 10


def test_get_cities_with_country(db, cities):
    "Test Filting cities by country"
    result = crud.get_cities(db, country="Country 2")
    assert len(result) == 21


def test_get_city_by_name(db, cities):
    county = crud.get_city_by_name(db, "City 99")
    assert county.id == 99

    assert crud.get_city_by_name(db, "City 9999") is None


def test_create_city(db, cities):
    "Add a new city (without id)."
    city = crud.create_city(db, CityCreate(name="foo", county_id=1, population=1111))
    assert city.name == "foo"
    assert city.population == 1111
    assert city.county_id == 1


def test_create_city_with_id(db, counties):
    "Add a new county with explicit id."
    city = crud.create_city(
        db, CityCreate(name="bar", county_id=1, population=999, id=100), city_id=9876
    )
    assert city.name == "bar"
    assert city.id == 9876
    assert city.population == 999
    assert city.county_id == 1

    # using an existing id must fail
    with pytest.raises((crud.CreationException, sqlalchemy.exc.IntegrityError)):
        crud.create_city(
            db, CityCreate(name="bar", population=999, county_id=1), city_id=9876
        )


def test_update_city(db, cities):
    "Update an existing city."
    city = crud.update_city(
        db, 1, city_name="FooBar 1", population=50, county_id=2
    )
    assert city.name == "FooBar 1"
    assert city.population == 50
    assert city.county_id == 2


def test_delete_city(db, cities):
    "Delete a city."
    city = crud.delete_city(db, 50)
    # delete returns the deleted object
    assert city.id == 50
    # check if delete city is really gone
    assert crud.get_city(db, 50) is None
