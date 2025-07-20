import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from fastapi import UploadFile
from io import BytesIO


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_prompt_manager():
    mock = AsyncMock()
    mock.get_prompt.return_value = ""
    return mock


@pytest.fixture
def mock_gemini_client():
    mock = AsyncMock()
    mock.generate_content.return_value = ""
    return mock


@pytest.fixture
def mock_mongo_service():
    mock = AsyncMock()
    mock.insert_document.return_value = {"inserted_id": "123"}
    return mock


@pytest.mark.asyncio
async def test_upload_file(test_client, mock_prompt_manager, mock_gemini_client, mock_mongo_service):
    app.dependency_overrides[get_prompt_manager] = lambda: mock_prompt_manager
    app.dependency_overrides[get_gemini_client] = lambda: mock_gemini_client
    app.dependency_overrides[get_mongo_service] = lambda: mock_mongo_service

    # Create a dummy file
    file_content = b"test content"
    file = UploadFile(filename="test.pdf", file=BytesIO(file_content), content_type="application/pdf")

    # Create form data
    form_data = {
        "collection_name": "test_collection",
        "file": (file.filename, file.file, file.content_type),
    }

    response = test_client.post("/upload_file", files={"file": form_data["file"]}, data={"collection_name": form_data["collection_name"]})

    assert response.status_code == 200
    assert response.json() == {"message": "File uploaded successfully", "data": {"collection_name": "test_collection", "filename": "test.pdf", "file_size": "0.00MB", "content_type": "application/pdf"}}

    app.dependency_overrides = {}


from app.prompts.prompts_manager import get_prompt_manager
from app.providers.llm.gemini import get_gemini_client
from app.utils.dependency import get_mongo_service