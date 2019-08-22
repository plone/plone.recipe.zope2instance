import sentry_sdk


def sdk_init(global_conf, dsn):
    def filter(app):
        sentry_sdk.init(dsn=dsn)
        return app
    return filter
