# -*- coding: utf-8 -*-

import daiquiri
from fastapi import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from pharma.settings import SETTINGS

LOGGER = daiquiri.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.skip_paths = [
            "/",
            "/favicon.ico",
            "/health/",
            SETTINGS.metrics_url,
            SETTINGS.docs_url,
            SETTINGS.openapi_url,
        ]

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        if scope["path"] in self.skip_paths:
            return await self.app(scope, receive, send)

        async def intercept_and_send(message: Message) -> None:
            """Intercept the response and log the relevant information."""
            request = Request(scope, receive=receive)
            if message["type"] == "http.response.start":
                LOGGER.info(
                    "User: '%s' IP: '%s' X-AMZN-TRACE-ID: '%s' %s %s %s",
                    request.headers.get("remote_user"),
                    request.headers.get("x-forwarded-for"),
                    request.headers.get("x-amzn-trace-id"),
                    request.method,
                    request.url.path,
                    message.get("status"),
                )

            await send(message)

        await self.app(scope, receive, intercept_and_send)
