import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_base_url(client: AsyncClient):
    response = await client.get('/users/')
    assert response.status_code == 200
    assert response.json() == []
