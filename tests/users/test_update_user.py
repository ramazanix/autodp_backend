import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user


@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient):
    """
    Trying to update user without auth
    """
    response = await client.post(
        "/users/", json={"username": "Alex", "password": "alex_password"}
    )
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.patch("/users/Alex/", json={"username": "not_Alex"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_authorized(client: AsyncClient):
    """
    Trying to update user with auth
    """
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch(
        "/users/Alex/", json={"username": "not_Alex"}, headers=headers
    )
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_Alex"

    response = await client.get("/users/Alex/", headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"

    response = await client.get("/users/not_Alex/", headers=headers)
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_Alex"


@pytest.mark.asyncio
async def test_update_user_blank_body(client: AsyncClient):
    """
    Trying to update user with blank body
    """
    user_data = {"username": "Joe", "password": "joe_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Joe"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch("/users/Alex/", json={}, headers=headers)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_too_small_username(client: AsyncClient):
    """
    Trying to update user's username to small value
    """
    user_data = {"username": "Joe", "password": "joe_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Joe"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch(
        "/users/Joe/", json={"username": "J"}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_username(client: AsyncClient):
    """
    Trying to update user's username to long value
    """
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch(
        "/users/Alex/", json={"username": "A" * 21}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_small_password(client: AsyncClient):
    """
    Trying to update user's password to small value
    """
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch(
        "/users/Alex/", json={"password": "A" * 33}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_password(client: AsyncClient):
    """
    Trying to update user's password to long value
    """
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.patch(
        "/users/Alex/", json={"password": "A" * 33}, headers=headers
    )
    assert response.status_code == 422
