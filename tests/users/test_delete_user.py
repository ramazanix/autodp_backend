import pytest
from httpx import AsyncClient


user_data = {"username": "username", "password": "password"}


@pytest.mark.asyncio
async def test_delete_current_user_unauthorized(client: AsyncClient, create_user):
    """
    Trying to delete current user without auth
    """
    response = await client.delete(f"/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_current_user_authorized(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to delete current user with auth
    """
    response = await client.delete(f"/users/me", headers=authorization_header)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_admin_unauthorized(client: AsyncClient, create_user):
    """
    Trying to delete user on admin path unauthorized
    """
    response = await client.delete(f'/admin/users/{user_data["username"]}')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_not_admin(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to delete user authorized via not admin
    """
    response = await client.delete(
        f'/admin/users/{user_data["username"]}', headers=authorization_header
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_admin(
    client: AsyncClient, create_user, authorization_header_admin
):
    """
    Trying to delete user authorized via admin
    """
    response = await client.delete(
        f'/admin/users/{user_data["username"]}', headers=authorization_header_admin
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_not_existed_user_admin(
    client: AsyncClient, create_user, authorization_header_admin
):
    """
    Trying to delete not existed user via admin
    """
    response = await client.delete(
        f"/admin/users/not_user", headers=authorization_header_admin
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"
