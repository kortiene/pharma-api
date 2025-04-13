# -*- coding: utf-8 -*-

import daiquiri
import uvicorn
from pharma.settings import SETTINGS

LOGGER = daiquiri.getLogger(__name__)


def api():
    """Execute the RESTful API Server."""
    daiquiri.setup(level=SETTINGS.log_level)  # type: ignore
    kwargs = {
        "host": "0.0.0.0",
        "port": SETTINGS.api_port,
        "workers": SETTINGS.workers,
        "log_level": SETTINGS.log_level.lower(),
    }
    if SETTINGS.environment == "local":
        kwargs["reload"] = True

    uvicorn.run("pharma.api:app", **kwargs)





