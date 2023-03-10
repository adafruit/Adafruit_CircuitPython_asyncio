"""Logging configuration."""

class Logger:
    def __init__(self, package):
        pass

    def debug(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        print(msg % args, kwargs)


# Name the logger after the package.
logger = Logger(None)
