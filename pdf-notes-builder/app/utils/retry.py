import functools
import logging
import time


class Retry:
    """
    Provides a retry decorator with exponential backoff.
    Parameters are pulled from the loaded config (retry.max_attempts,
    retry.delay_seconds, retry.backoff_multiplier) rather than hardcoded.
    """

    def __init__(self, max_attempts, delay_seconds, backoff_multiplier, logger=None):
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.logger = logger or logging.getLogger("invoice_pipeline")

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            delay = self.delay_seconds
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt >= self.max_attempts:
                        self.logger.error(
                            "Function '%s' failed after %d attempts: %s",
                            func.__name__, attempt, exc,
                        )
                        raise
                    self.logger.info(
                        "Attempt %d/%d for '%s' failed (%s). Retrying in %ss...",
                        attempt, self.max_attempts, func.__name__, exc, delay,
                    )
                    time.sleep(delay)
                    delay *= self.backoff_multiplier
                    attempt += 1
        return wrapper
