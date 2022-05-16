from cities import crud
from cities.schemas import CountyCreate
import pytest
import sqlalchemy.exc


def test_get_county(db, counties):
    "Test the get_county function."
    assert crud.get_county(db, 1).name == "County 1"
    assert crud.get_county(db, 99).name == "County 99"


def test_get_counties(db, counties):
    """Get all countries."""
    # Limit is 100 by default; we do not set a limit.
    result = crud.get_counties(db)
    assert len(result) == 100

    # Test if result is ordered by name
    assert result[0].id == 1
    assert result[1].id == 10
    assert result[2].id == 100

    # Set limit to 20
    result = crud.get_counties(db, limit=20)
    assert len(result) == 20
    assert result[0].id == 1

    # Set limit to 20 and skip 40
    result = crud.get_counties(db, skip=40, limit=20)
    assert len(result) == 20
    # because we sort by name and 5 later names slip in so the 41th entry has id 36
    assert result[0].id == 36


def test_get_counties_with_q(db, counties):
    "q= searches for substring in county.name."
    result = crud.get_counties(db, q='ty 8')
    # 8 and 80 to 89 = 11
    assert len(result) == 11

def test_counties_with_country(db, counties):
    result = crud.get_counties(db, country="Country 2")
    assert len(result) == 10

def test_get_county_by_name(db, counties):
    county = crud.get_county_by_name(db, "County 99")
    assert county.id == 99

    assert crud.get_county_by_name(db, "County 9999") is None


def test_create_county(db, counties):
    "Add a new county (without id)."
    county = crud.create_county(db, CountyCreate(name="foo", country_id=1))
    assert county.name == "foo"


def test_create_county_with_id(db, counties):
    "Add a new county with explicit id."
    county = crud.create_county(db, CountyCreate(name="bar", country_id=1, id=1000))
    assert county.name == "bar"
    assert county.id == 1000

    # using an existing id must fail
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        crud.create_county(db, CountyCreate(name="bar", country_id=1, id=1000))


def test_update_county(db, counties):
    "Update an existing county."
    county = crud.update_county(db, 1, CountyCreate(name="FooBar 1", country_id=1))
    assert county.name == "FooBar 1"
