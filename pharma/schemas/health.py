# -*- coding: utf-8 -*-


import daiquiri
from pydantic import BaseModel

LOGGER = daiquiri.getLogger(__name__)


class MongoServerInfotModel(BaseModel):
    """A model for server_info response."""

    ok: float
    version: str
