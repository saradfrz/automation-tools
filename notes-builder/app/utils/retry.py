import logging
import time
from functools import wraps


def retry(max_attempts: int = 3, delay_seconds: float = 1.0, exceptions=(Exception,)):
    """
    Decorator factory that retries the wrapped function on failure.

    All behavior is parametrized by the caller (typically sourced from
    config.json) rather than hardcoded here.

    :param max_attempts: total number of attempts before giving up.
    :param delay_seconds: seconds to wait between attempts.
    :param exceptions: exception types that should trigger a retry.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("invoice_pipeline")
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt >= max_attempts:
                        logger.error(
                            "'%s' failed after %d attempt(s): %s",
                            func.__name__,
                            attempt,
                            exc,
                        )
                        raise
                    logger.warning(
                        "'%s' failed on attempt %d/%d: %s. Retrying in %.1fs...",
                        func.__name__,
                        attempt,
                        max_attempts,
                        exc,
                        delay_seconds,
                    )
                    time.sleep(delay_seconds)
                    attempt += 1

        return wrapper

    return decorator
