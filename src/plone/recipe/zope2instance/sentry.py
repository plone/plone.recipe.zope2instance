import logging
import sentry_sdk
import sys
from sentry_sdk.hub import Hub
from sentry_sdk.integrations.logging import (
    LoggingIntegration,
    ignore_logger,
    DEFAULT_LEVEL,
    DEFAULT_EVENT_LEVEL,
    EventHandler,
    _can_record,
    _logging_to_event_level,
    _extra_from_record)

from sentry_sdk.utils import (
    current_stacktrace,
    to_string,
    capture_internal_exceptions,
    event_from_exception)


class ZopeEventHandler(EventHandler):

    def _emit(self, record):
        if not _can_record(record):
            return

        hub = Hub.current
        if hub.client is None:
            return

        client_options = hub.client.options
        if not record.exc_info:
            record.exc_info = sys.exc_info()
        # exc_info might be None or (None, None, None)
        if record.exc_info is not None and record.exc_info[0] is not None:
            event, hint = event_from_exception(
                record.exc_info,
                client_options=client_options,
                mechanism={"type": "logging", "handled": True},
            )
        elif record.exc_info and record.exc_info[0] is None:
            event = {}
            hint = {}
            with capture_internal_exceptions():
                event["threads"] = {
                    "values": [
                        {
                            "stacktrace": current_stacktrace(
                                client_options["with_locals"]
                            ),
                            "crashed": False,
                            "current": True,
                        }
                    ]
                }
        else:
            event = {}
            hint = {}

        hint["log_record"] = record

        event["level"] = _logging_to_event_level(record.levelname)
        event["logger"] = record.name
        event["logentry"] = {
            "message": to_string(record.msg),
            "params": record.args}
        event["extra"] = _extra_from_record(record)

        hub.capture_event(event, hint=hint)


class ZopeSentryLogging(LoggingIntegration):

    def __init__(self, level=DEFAULT_LEVEL, event_level=DEFAULT_EVENT_LEVEL):
        LoggingIntegration.__init__(self, level, event_level)
        if event_level is not None:
            self._handler = ZopeEventHandler(level=event_level)


def sdk_init(
        global_conf,
        dsn,
        level='INFO',
        event_level='ERROR',
        ignorelist=''):
    sentry_logging = ZopeSentryLogging(
        level=logging.__dict__[level],
        event_level=logging.__dict__[event_level]
    )
    for logger in ignorelist.split():
        ignore_logger(logger)

    def filter(app):
        sentry_sdk.init(dsn=dsn, integrations=[sentry_logging])
        return app
    return filter
