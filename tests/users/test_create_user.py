import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user, users


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post('/users/',
                                 json={'username': 'Paul', 'password': 'paul_password'})
    assert response.status_code == 201

    assert exact_schema(user) == response.json()

    assert response.json().get('username') == 'Paul'


@pytest.mark.asyncio
async def test_create_couple_users(client: AsyncClient):
    response = await client.post('/users/',
                                 json={'username': 'Joe', 'password': 'joe_password'})
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get('username') == 'Joe'

    response = await client.post('/users/',
                                 json={'username': 'Tom', 'password': 'tom_password'})

    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get('username') == 'Tom'

    response = await client.get('/users/')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert exact_schema(users) == response.json()


@pytest.mark.asyncio
async def test_create_blank_user_data(client: AsyncClient):
    response = await client.post('/users/', json={})
    assert response.status_code == 422


    # response = await client.post('/users/', json={'a': 'b'})
    # assert response.status_code == 422
    #
    # response = await client.post('/users/', json={'username': ''})
    # assert response.status_code == 422
    #
    # response = await client.post('/users/', json={'password': ''})
    # assert response.status_code == 422
    #
    # response = await client.post('/users/', json={'username': '', 'password': ''})
    # assert response.status_code == 422
    #
    # response = await client.post('/users/', json={'username': 'Alex', 'password': '123'})
    # assert response.status_code == 422
