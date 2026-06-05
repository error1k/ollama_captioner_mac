import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_index_returns_html(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.anyio
async def test_list_models_online(client):
    mock_model = MagicMock()
    mock_model.model = "gemma3:latest"
    mock_response = MagicMock()
    mock_response.models = [mock_model]

    with patch("app.ollama.list", return_value=mock_response):
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "gemma3:latest" in data["models"]


@pytest.mark.anyio
async def test_list_models_offline(client):
    with patch("app.ollama.list", side_effect=Exception("Connection refused")):
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "offline"
        assert data["models"] == []


@pytest.mark.anyio
async def test_caption_missing_model(client):
    response = await client.post("/api/caption", data={}, files={})
    assert response.status_code == 400


@pytest.mark.anyio
async def test_caption_missing_file(client):
    response = await client.post(
        "/api/caption",
        data={"model_name": "gemma3:latest", "prompt": "Describe this"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_caption_success(client):
    with patch("app.call_ollama_api", return_value="A photo of a cat"):
        fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = await client.post(
            "/api/caption",
            data={"model_name": "gemma3:latest", "prompt": "Describe this"},
            files={"file": ("test.png", fake_image, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["caption"] == "A photo of a cat"
