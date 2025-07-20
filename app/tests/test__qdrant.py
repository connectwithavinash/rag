import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from qdrant_client import models


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_qdrant_service():
    mock = AsyncMock()
    mock.create_collection.return_value = True
    mock.upsert_points.return_value = {"operation_id": 1}
    mock.retrieve_points.return_value = [models.ScoredPoint(id=1, version=1, score=1.0, vector=[0.0, 0.0], payload={})]
    mock.search_points.return_value = [models.ScoredPoint(id=1, version=1, score=1.0, vector=[0.0, 0.0], payload={})]
    mock.delete_points.return_value = {"operation_id": 1}
    return mock


@pytest.mark.asyncio
async def test_create_qdrant_collection(test_client, mock_qdrant_service):
    app.dependency_overrides[get_qdrant_service] = lambda: mock_qdrant_service
    response = test_client.post("/qdrant/create_collection?collection_name=test_collection&vector_size=128")
    assert response.status_code == 200
    assert response.json() == {"message": "Qdrant collection 'test_collection' created successfully.", "status": "success"}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_upsert_qdrant_points(test_client, mock_qdrant_service):
    app.dependency_overrides[get_qdrant_service] = lambda: mock_qdrant_service
    points = [models.PointStruct(id=1, vector=[0.0, 0.0], payload={})]
    response = test_client.post("/qdrant/upsert_points?collection_name=test_collection", json=points)
    assert response.status_code == 200
    assert response.json() == {"message": "Points upserted to 'test_collection' successfully.", "status": "success", "operation_info": {"operation_id": 1}}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_retrieve_qdrant_points(test_client, mock_qdrant_service):
    app.dependency_overrides[get_qdrant_service] = lambda: mock_qdrant_service
    response = test_client.get("/qdrant/retrieve_points?collection_name=test_collection&ids=[1]")
    assert response.status_code == 200
    assert response.json() == {"message": "Points retrieved from 'test_collection' successfully.", "status": "success", "points": [{"id": 1, "version": 1, "score": 1.0, "vector": [0.0, 0.0], "payload": {}}]}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_search_qdrant_points(test_client, mock_qdrant_service):
    app.dependency_overrides[get_qdrant_service] = lambda: mock_qdrant_service
    query_vector = [0.0, 0.0]
    response = test_client.post("/qdrant/search_points?collection_name=test_collection", json=query_vector)
    assert response.status_code == 200
    assert response.json() == {"message": "Search in 'test_collection' returned results successfully.", "status": "success", "result": [{"id": 1, "version": 1, "score": 1.0, "vector": [0.0, 0.0], "payload": {}}]}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_delete_qdrant_points(test_client, mock_qdrant_service):
    app.dependency_overrides[get_qdrant_service] = lambda: mock_qdrant_service
    points_selector = models.PointIdsList(points=[1])
    response = test_client.delete("/qdrant/delete_points?collection_name=test_collection", json=points_selector.dict())
    assert response.status_code == 200
    assert response.json() == {"message": "Points deleted from 'test_collection' successfully.", "status": "success", "operation_info": {"operation_id": 1}}
    app.dependency_overrides = {}


from app.utils.dependency import get_qdrant_service