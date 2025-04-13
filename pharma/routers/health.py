# -*- coding: utf-8 -*-

import daiquiri
from fastapi import APIRouter, Request

from pharma.schemas.health import MongoServerInfotModel

LOGGER = daiquiri.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", include_in_schema=False)
async def health(request: Request) -> MongoServerInfotModel:
    server_info = await request.app.mongodb_client.server_info()
    return server_info
