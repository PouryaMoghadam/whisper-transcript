from app.utils.warnings_filter import filter_warnings

filter_warnings()

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse

from app.platform.config import Config
from app.platform.db import engine
from app.models import Base
from app.utils.docs import generate_db_schema, save_openapi_json
from app.routers.service import service_router

load_dotenv()


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    save_openapi_json(app)
    generate_db_schema(Base.metadata.tables.values())
    yield


tags_metadata = [
    {
        "name": "Speech-2-Text",
        "description": "Operations related to transcript",
    },
    {
        "name": "Speech-2-Text services",
        "description": "Individual services for transcript",
    },
    {
        "name": "Tasks Management",
        "description": "Manage tasks.",
    },
]


app = FastAPI(
    title="VIDEO AI REST service",
    description=f"""
    ## Supported file extensions:
    AUDIO_EXTENSIONS = {Config.AUDIO_EXTENSIONS}
    VIDEO_EXTENSIONS = {Config.VIDEO_EXTENSIONS}
    """,
    version="0.0.1",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Include routers
app.include_router(service_router)
# app.include_router(task.task_router)
# app.include_router(stt_services.service_router)

# app.include_router("/")

base_router = APIRouter()


@base_router.get("base", response_class=RedirectResponse, include_in_schema=False)
async def index():
    return JSONResponse({"status": "success"})
