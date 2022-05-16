from cities import crud
from cities.schemas import CountryCreate
import pytest
import sqlalchemy.exc

def test_get_country(db, countries):
    "Test the get_country function."
    assert crud.get_country(db, 1).name == "Country 1"
    assert crud.get_country(db, 99).name == "Country 99"

def test_get_countries(db, countries):
    """Get all countries.
    """
    # Limit is 100 by default; we do not set a limit.
    result = (crud.get_countries(db))
    assert len(result) == 100

    # Test if result is ordered by name
    assert result[0].id == 1
    assert result[1].id == 10
    assert result[2].id == 100

    # Set limit to 20
    result = crud.get_countries(db, limit=20)
    assert len(result) == 20
    assert result[0].id == 1

    # Set limit to 20 and skip 40
    result = crud.get_countries(db, skip=40, limit=20)
    assert len(result) == 20
    # because we sort by name and 5 later names slip in so the 41th entry has id 36
    assert result[0].id == 36 

def test_get_countries_with_q(db, countries):
    "q searches for substring in Country.name"
    result = crud.get_countries(db, q='try 99')
    assert len(result) == 1

def test_get_country_by_name(db, countries):
    country = crud.get_country_by_name(db, "Country 99")
    assert country.id == 99

    assert crud.get_country_by_name(db, "Country 9999") is None


def test_create_country(db, countries):
    "Add a new Country (without id)."
    country = crud.create_country(db, CountryCreate(name="foo"))
    assert country.name == "foo"

def test_create_country_with_id(db, countries):
    "Add a new Country with explicit id."
    country = crud.create_country(db, CountryCreate(name="bar", id=1000))
    assert country.name == "bar"
    assert country.id == 1000

    # using an existing id must fail
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        crud.create_country(db, CountryCreate(name="bar", id=1000))

def test_update_country(db, countries):
    "Update an existing country."
    country = crud.update_country(db, 1, CountryCreate(name="FooBar 1"))
    assert country.name == "FooBar 1"

