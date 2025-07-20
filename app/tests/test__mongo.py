import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_mongo_service():
    mock = AsyncMock()
    mock.create_collection_if_not_exists.return_value = (AsyncMock(), True)
    mock.insert_document.return_value = {"inserted_id": "123"}
    mock.update_document.return_value = {"updated_count": 1}
    mock.delete_document.return_value = {"deleted_count": 1}
    return mock


@pytest.mark.asyncio
async def test_create_new_collection(test_client, mock_mongo_service):
    app.dependency_overrides[get_mongo_service] = lambda: mock_mongo_service
    response = test_client.post("/mongo/create_collection?collection_name=test_collection")
    assert response.status_code == 200
    assert response.json() == {"message": "Collection 'test_collection' created successfully.", "data": {"collection": None, "created": True}}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_insert_data(test_client, mock_mongo_service):
    app.dependency_overrides[get_mongo_service] = lambda: mock_mongo_service
    response = test_client.post("/mongo/create_document?collection_name=test_collection", json={"key": "value"})
    assert response.status_code == 200
    assert response.json() == {"message": "Document inserted successfully.", "data": {"inserted_id": "123"}}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_update_data(test_client, mock_mongo_service):
    app.dependency_overrides[get_mongo_service] = lambda: mock_mongo_service
    response = test_client.put("/mongo/update_document?collection_name=test_collection", json={"filter": {"key": "value"}, "update_data": {"$set": {"key": "new_value"}}})
    assert response.status_code == 200
    assert response.json() == {"message": "Document updated successfully.", "data": {"updated_count": 1}}
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_delete_data(test_client, mock_mongo_service):
    app.dependency_overrides[get_mongo_service] = lambda: mock_mongo_service
    response = test_client.delete("/mongo/delete_document?collection_name=test_collection", json={"filter": {"key": "value"}})
    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted successfully.", "data": {"deleted_count": 1}}
    app.dependency_overrides = {}


from app.utils.dependency import get_mongo_service