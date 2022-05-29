"""Test endpoints defined in routers/city.
"""

# pylint: disable=W0613


def test_get_with_id(client, cities):
    "Test if cities/<id> works."
    response = client.get("/cities/1")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["name"] == "City 1"
    assert result["population"] == 10

    assert result["county"]["name"] == "County 1"
    assert result["county"]["id"] == 1
    assert result["county"]["link"] == "http://testserver/counties/1"
    assert result["country"]["name"] == "Country 1"
    assert result["country"]["id"] == 1
    assert result["country"]["link"] == "http://testserver/countries/1"


def test_get_for_non_exisiting_id(client, cities):
    "Request to non exsiting city must return 404."
    response = client.get("/cities/987654")
    assert response.status_code == 404


def test_options_with_id(client, cities):
    "Test the OPTIONS method against /cities/<id>)."
    response = client.options("/cities/1")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 5
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "PUT" in allowed
    assert "OPTIONS" in allowed
    assert "DELETE" in allowed


def test_put_update(client, cities):
    "Test put to update an existing city."
    response = client.put(
        "/cities/1", json={"name": "BarFoo", "population": 77, "county_id": 1}
    )
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "BarFoo"
    assert response.json()["link"] == "http://testserver/cities/1"
    assert response.json()["county"]["id"] == 1
    assert response.json()["county"]["name"] == "County 1"
    assert response.json()["county"]["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"


def test_put_update_new_id_must_fail(client, cities):
    "Updates must not replace the id."
    response = client.put(
        "/cities/1",
        json={"id": 9999, "name": "BarFoo", "population": 77, "county_id": 1},
    )
    assert response.status_code == 422


def test_put_update_fail(client, cities):
    "Updating an existing city with a non existing county_id must fail."
    response = client.put(
        "/cities/1", json={"name": "BarFoo", "population": 77, "county_id": 99999}
    )
    assert response.status_code == 422


def test_put_create(client, cities):
    "Test put to update an existing city."
    response = client.put(
        "/cities/9123", json={"name": "Foo", "population": 77, "county_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 9123
    assert response.json()["name"] == "Foo"
    assert response.json()["link"] == "http://testserver/cities/9123"
    assert response.json()["county"]["id"] == 1
    assert response.json()["county"]["name"] == "County 1"
    assert response.json()["county"]["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"


def test_put_create_fail(client, cities):
    "Creating a new city via put with a non existing county_id must fail."
    response = client.put(
        "/cities/98765", json={"name": "BarFoo", "population": 77, "county_id": 99999}
    )
    assert response.status_code == 422


def test_delete(client, cities):
    "Delete as city."
    response = client.delete("/cities/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["link"] is None  # Nothing left to link to
    assert response.json()["county"]["id"] == 1
    assert response.json()["county"]["name"] == "County 1"
    assert response.json()["county"]["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"


def test_delete_non_existing(client, cities):
    "Delete a non exisiting city."
    response = client.delete("/cities/98765")
    assert response.status_code == 404


def test_patch_name(client, cities):
    "Test if patching name works."
    response = client.patch("/cities/1", json={"name": "Foo"})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Foo"
    assert response.json()["population"] == 10
    assert response.json()["county"]["id"] == 1


def test_patch_population(client, cities):
    "Test if patching name works."
    response = client.patch("/cities/1", json={"population": 1000000})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "City 1"
    assert response.json()["population"] == 1000000
    assert response.json()["county"]["id"] == 1


def test_patch_county(client, cities):
    "Test if patching name works."
    response = client.patch("/cities/1", json={"county_id": 2})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "City 1"
    assert response.json()["population"] == 10
    assert response.json()["county"]["id"] == 2


def test_patch_all(client, cities):
    "Test if patching all allowed values works."
    response = client.patch(
        "/cities/1", json={"name": "FooBar", "population": 50000, "county_id": 2}
    )
    assert response.json()["id"] == 1
    assert response.json()["name"] == "FooBar"
    assert response.json()["population"] == 50000
    assert response.json()["county"]["id"] == 2


def test_patch_non_existing(client, cities):
    "Patching a non existing cities leads to 404."
    response = client.patch("/cities/987654", json={"name": "Foo"})
    assert response.status_code == 404


def test_patch_non_existing_county(client, cities):
    "Patching a non existing cities leads to 404."
    response = client.patch("/cities/1", json={"county_id": 987654})
    assert response.status_code == 422
