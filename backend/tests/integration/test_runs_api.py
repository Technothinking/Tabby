import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_and_get_run():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create
        response = await ac.post("/api/v1/runs", json={
            "goal": "Test run orchestration",
            "max_steps": 20
        })
        assert response.status_code == 201
        data = response.json()
        assert data["goal"] == "Test run orchestration"
        assert data["status"] == "pending"
        run_id = data["id"]
        
        # Get
        get_resp = await ac.get(f"/api/v1/runs/{run_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["id"] == run_id
        assert get_data["status"] == "pending"
        assert get_data["steps"] == []
