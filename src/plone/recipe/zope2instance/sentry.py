import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger


def sdk_init(
        global_conf,
        dsn,
        level='INFO',
        event_level='ERROR',
        ignorelist=''):
    sentry_logging = LoggingIntegration(
        level=logging.__dict__[level],
        event_level=logging.__dict__[event_level]
    )
    for logger in ignorelist.split():
        ignore_logger(logger)

    def filter(app):
        sentry_sdk.init(dsn=dsn, integrations=[sentry_logging])
        return app
    return filter
