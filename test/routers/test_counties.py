"""Test endpoints defined in routers/counties.
"""

# pylint: disable=W0613


def test_get(client, counties):
    "Test unparametrized request to /counties"
    response = client.get("/counties")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    assert results[0]["id"] == 1
    assert results[1]["id"] == 10

    # check response format
    first_result = results[0]
    assert first_result["id"] == 1
    assert first_result["name"] == "County 1"
    assert first_result["link"] == "http://testserver/counties/1"


def test_get_with_paging(client, counties):
    "Test if explicit paging works."
    response = client.get("/counties?start=41&size=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5
    assert result[0]["id"] == 36


def test_get_with_invalid_params(client, counties):
    "Test invalid parameters."
    # start= must be 1 or greater.
    response = client.get("/counties?start=0")
    assert response.status_code == 422

    # size must be 1 or greater
    response = client.get("/counties?size=0")
    assert response.status_code == 422


def test_get_with_param_q(client, counties):
    "Test if ?q= works"
    response = client.get("/counties?q=ty+5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 11
    assert result[0]["name"] == "County 5"
    assert result[1]["name"] == "County 50"


def test_get_with_param_country(client, counties):
    "Test if ?country= works"
    response = client.get("/counties?country=Country+2")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 10


def test_head(client, counties):
    "Test a head_request against /counties"
    response = client.head("/counties/")
    assert response.status_code == 200


def test_options_counties(client, counties):
    "Test the OPTIONS method against /counties."
    response = client.options("/counties")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "POST" in allowed
    assert "OPTIONS" in allowed


def test_post(client, countries):
    "Test POST to create a new County."
    response = client.post("/counties/", json={"name": "FooBar", "country_id": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "FooBar"
    assert response.json()["id"]
    assert response.json()["link"]
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county


def test_post_with_id(client, countries):
    "Test POST to create a new County with a pre defined id."
    response = client.post(
        "/counties/", json={"id": 99, "name": "FooBar", "country_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 99
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"] == "http://testserver/counties/99"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county


def test_post_with_existing_id(client, counties):
    "POST with an exisiting id must raise Error."
    response = client.post(
        "/counties/", json={"id": 1, "name": "FooBar", "country_id": 1}
    )
    assert response.status_code == 400


def test_post_with_non_exisiting_country_id(client, counties):
    "POST with country_id without country must raise Error."
    response = client.post("/counties/", json={"name": "FooBar", "country_id": 9999})
    assert response.status_code == 400
