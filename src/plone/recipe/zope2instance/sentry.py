from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.logging import LoggingIntegration

import logging
import sentry_sdk


def sdk_init(
    global_conf,
    dsn,
    level="INFO",
    event_level="ERROR",
    ignorelist="",
    max_value_length="",
):
    sentry_logging = LoggingIntegration(
        level=logging.__dict__[level], event_level=logging.__dict__[event_level]
    )
    for logger in ignorelist.split():
        ignore_logger(logger)
    if max_value_length == "":
        # Fall back to sentry-sdk default of 1024
        max_value_length = None
    else:
        # This will raise on startup if the provided value is invalid. Fine.
        max_value_length = int(max_value_length)

    def filter(app):
        sentry_sdk.init(
            dsn=dsn, integrations=[sentry_logging], max_value_length=max_value_length
        )
        return app

    return filter
