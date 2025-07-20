from qdrant_client.models import PayloadSchemaType

COLLECTION_PAYLOAD_INDEX_CONFIG = {
    "budgets": {
        "uploaded_date": PayloadSchemaType.DATETIME,
        "filename": PayloadSchemaType.KEYWORD,
        "document_id": PayloadSchemaType.KEYWORD,
    }
    }
