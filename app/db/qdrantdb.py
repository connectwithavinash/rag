import qdrant_client
from ..core.config import get_settings
from ..services.qdrant_services import QdrantService
from fastapi import FastAPI
from ..core.logging import get_logger

logger = get_logger()

async def initialise_qdrant(app: FastAPI):
    settings = get_settings()
    client = qdrant_client.AsyncQdrantClient(settings.qdrant_url)
    client.set_model(settings.qdrant_dense_model)
    client.set_sparse_model(settings.qdrant_sparse_model)
    try:
        # Attempt to get collections to check connectivity
        await client.get_collections()
        logger.info("Qdrant Connection Successful")

        # Warm-up model to avoid cold start latency
        warmup_collection = "_warmup"
        await client.add(
            collection_name=warmup_collection,
            documents=["hello"],
            metadata=[{"source": "warmup"}],
        )

        await client.query(
            collection_name=warmup_collection,
            query_text="test",
            limit=1
        )

        logger.info("Qdrant model warm-up completed.")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise RuntimeError(f"Failed to connect to Qdrant: {e}")
    
    qdrant_service = QdrantService(client)
    app.state.qdrant_service_client = qdrant_service
    app.state.qdrant_client = client
    
    return client

async def close_qdrant_connection(app: FastAPI):
    if hasattr(app.state,'qdrant_client') and app.state.qdrant_client:
        await app.state.qdrant_client.close()
        logger.info("Qdrant Connnection Close Sucessfully")