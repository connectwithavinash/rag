from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .core.logging import get_logger
import time
from .db.mongodb import initialise_mongo, close_mongo_connection
from .db.qdrantdb import initialise_qdrant, close_qdrant_connection
from .api.v1.routers import file_upload,_mongo
from .providers.llm.gemini import initialise_gemini
from .providers.llm.openai import initialise_azure_openai
from .schemas.error_response import ErrorResponse
from .api.v1.routers import router as api_v1_router
# from prometheus_fastapi_instrumentator import Instrumentator
# from opentelemetry import trace
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


logger = get_logger()

# Set up OpenTelemetry
# resource = Resource.create({
#     SERVICE_NAME: "uv-example-service"
# })

# tracer_provider = TracerProvider(resource=resource)
# tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
# trace.set_tracer_provider(tracer_provider)


@asynccontextmanager
async def lifespan(app : FastAPI):
    #starting script
    await initialise_mongo(app)
    initialise_gemini(app) 
    await initialise_qdrant(app)
    initialise_azure_openai(app)

    yield
    
    await close_qdrant_connection(app)
    await close_mongo_connection(app)
    #closing script


app = FastAPI(lifespan=lifespan)

# Instrument FastAPI for tracing
# FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

# Instrument FastAPI for Prometheus metrics
# Instrumentator().instrument(app).expose(app)

app.include_router(api_v1_router, prefix="/api/v1")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, status_code=exc.status_code, error_type=exc.detail).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_type="Internal Server Error").model_dump()
    )


@app.middleware('http')
async def processing_time(request: Request, call_next ):
    start_time = time.perf_counter()
    content_type  = request.headers.get("content-type",'')
    is_file_upload = 'multipart/form-data' in content_type

    if is_file_upload:
        body_str = "<File upload - not read>"
        logger.info(f"Skipping body logging for file upload")
    else:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8', errors='ignore')
        logger.info(f"{body_str}")

        request = Request(request.scope, receive=lambda: {'type': 'http.request', 'body': body_bytes})

    response = await call_next(request)

    end_time = time.perf_counter()

    total_time = end_time - start_time

    logger.info(f"{request.method} {request.url} processed in {total_time: 4f}")
    logger.info(f"Request parameters are: {body_str}")
    return response
    

# @app.post("/")
# async def main(settings: Annotated[config.Settings, Depends(config.get_settings)]):
#     return {"response" :f"{settings.app_name}"}



# if __name__ == "__main__":
#     uvicorn.run(app,host="0.0.0.0")