"""Test endpoints defined in routers/county.
"""
# pylint: disable=W0613


def test_get_with_id(client, cities):
    "Test if county/<id> works."
    response = client.get("/counties/1")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["name"] == "County 1"

    assert len(result["cities"]) == 9
    assert result["cities"][0]["id"] == 1
    assert result["cities"][0]["name"] == "City 1"
    assert result["cities"][0]["link"] == "http://testserver/cities/1"


def test_get_with_non_existing_id(client, counties):
    "Requesting a non existing county must return 404."
    response = client.get("/counties/98765")
    assert response.status_code == 404


def test_options_with_id(client, counties):
    "Test the OPTIONS method against /counties/<id>)."
    response = client.options("/counties/1")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "PUT" in allowed
    assert "OPTIONS" in allowed


def test_put_update(client, cities):
    "Test put to update an existing county."
    response = client.put("/counties/1", json={"name": "BarFoo", "country_id": 1})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "BarFoo"
    assert response.json()["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert len(response.json()["cities"]) == 9
    city1 = response.json()["cities"][0]
    assert city1["id"] == 1
    assert city1["name"] == "City 1"
    assert city1["link"] == "http://testserver/cities/1"


def test_put_update_fail(client, counties):
    "Updating an existing county with a non existing country_id must fail."
    response = client.put("/counties/1", json={"name": "BarFoo", "country_id": 99999})
    assert response.status_code == 400


def test_put_update_new_id_must_fail(client, counties):
    "Updates must not replace the id."
    response = client.put(
        "/counties/1", json={"id": 9999, "name": "BarFoo", "country_id": 1}
    )
    assert response.status_code == 400


def test_put_create(client, counties):
    "Test put to update an existing county."
    response = client.put("/counties/9123", json={"name": "Foo", "country_id": 1})
    assert response.status_code == 201
    assert response.json()["id"] == 9123
    assert response.json()["name"] == "Foo"
    assert response.json()["link"] == "http://testserver/counties/9123"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county


def test_put_create_fail(client, cities):
    "Creating a new county via put with a non existing country_id must fail."
    response = client.put(
        "/counties/98765", json={"name": "BarFoo", "country_id": 99999}
    )
    assert response.status_code == 400


def test_delete(client, counties):
    "Delete is not implemented for counties."
    response = client.delete("/counties/1")
    assert response.status_code == 405


def test_patch_name(client, cities):
    "Test if patching name works."
    response = client.patch("/counties/1", json={"name": "Foo"})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Foo"
    assert response.json()["country"]["id"] == 1


def test_patch_country(client, counties):
    "Test if patching name works."
    response = client.patch("/counties/1", json={"country_id": 2})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "County 1"
    assert response.json()["country"]["id"] == 2


def test_patch_all(client, counties):
    "Test if patching all allowed values works."
    response = client.patch("/counties/1", json={"name": "FooBar", "country_id": 2})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "FooBar"
    assert response.json()["country"]["id"] == 2


def test_patch_non_existing(client, counties):
    "Patching a non existing counties leads to 404."
    response = client.patch("/counties/987654", json={"name": "Foo"})
    assert response.status_code == 404


def test_patch_non_existing_country(client, counties):
    "Patching a non existing county leads to 404."
    response = client.patch("/counties/1", json={"country_id": 987654})
    assert response.status_code == 422
