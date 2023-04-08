import pytest
from pytest_schema import exact_schema
from httpx import AsyncClient
from .schemas import user


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient):
    """
    Trying to delete user without auth
    """
    response = await client.post(
        "/users/", json={"username": "Alex", "password": "alex_password"}
    )
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.delete("/users/Alex/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_authorized(client: AsyncClient):
    """
    Trying to delete user with auth
    """
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.delete("/users/Alex/", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_not_existed_user(client: AsyncClient):
    """
    Trying to delete not existed user
    """
    user_data = {"username": "Tom", "password": "tom_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Tom"

    response = await client.post("/auth/login/", json=user_data)
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.delete("/users/Alex/", headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"
