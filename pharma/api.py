# -*- coding: utf-8 -*-


import logging
from contextlib import asynccontextmanager

import daiquiri
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from starlette_exporter import PrometheusMiddleware, handle_metrics

from pharma.middleware.logging import LoggingMiddleware
from pharma.routers import health as health_router
from pharma.routers import agent as agent_router
from pharma.routers import llm as llm_agent
from pharma.settings import SETTINGS

LOGGER = daiquiri.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Defines the startup and shutdown events."""
    # Startup event
    await startup_db_client(application)

    yield

    # Shutdown event
    await shutdown_db_client(application)


app = FastAPI(
    title=f"{SETTINGS.app} API",
    docs_url=SETTINGS.docs_url,
    openapi_url=SETTINGS.openapi_url,
    version=SETTINGS.version,
    lifespan=lifespan,  # type: ignore
)

app.include_router(health_router.router)
app.include_router(agent_router.router)
app.include_router(llm_agent.router)
app.add_route(SETTINGS.metrics_url, handle_metrics)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.allow_origins,
    allow_credentials=SETTINGS.allow_credentials,
    allow_methods=SETTINGS.allow_methods,
    allow_headers=SETTINGS.allow_headers,
)

#  For parameters supported by the PrometheusMiddleware,
#  Refer: https://github.com/stephenhillier/starlette_exporter#options
app.add_middleware(
    PrometheusMiddleware,
    app_name=SETTINGS.app,
    prefix="pharma",
    labels={"service_version": SETTINGS.version},
    filter_unhandled_paths=True,
    group_paths=True,
    skip_paths=[
        "/",
        "/favicon.ico",
        SETTINGS.metrics_url,
        SETTINGS.docs_url,
        SETTINGS.openapi_url,
    ],
)
app.add_middleware(LoggingMiddleware)
daiquiri.setup(level=SETTINGS.log_level)  # type: ignore
logging.getLogger("httpx").setLevel("WARNING")
logging.getLogger("httpcore").setLevel("WARNING")
logging.getLogger("multipart").setLevel("WARNING")


async def startup_db_client(application: FastAPI):
    """Connect to MongoDB and create indexes."""
    mongodb_client = AsyncIOMotorClient(SETTINGS.mongodb_url)
    mongodb = mongodb_client[SETTINGS.mongodb_name]
    application.mongodb_client = mongodb_client
    application.mongodb = mongodb


async def shutdown_db_client(application: FastAPI):
    """Disconnect from MongoDB."""
    application.mongodb_client.close()  # type: ignore


@app.get("/", include_in_schema=False)
def read_root():
    return {
        "app": f"{SETTINGS.app} API",
        "version": SETTINGS.version,
        "docs": SETTINGS.docs_url,
        "environment": SETTINGS.environment,
    }
