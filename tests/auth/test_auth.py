import pytest
from pytest_schema import exact_schema
from .schemas import login
from ..users.schemas import user
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_not_existed_user(client: AsyncClient):
    response = await client.post(
        "/auth/login/", json={"username": "not_exists", "password": "12345678"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"


@pytest.mark.asyncio
async def test_auth_existed_user(client: AsyncClient):
    user_data = {"username": "Alex", "password": "alex_password"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Alex"

    response = await client.post("/auth/login/", json=user_data)
    assert response.status_code == 200
    assert exact_schema(login) == response.json()
