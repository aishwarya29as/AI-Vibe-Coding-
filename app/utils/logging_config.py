import logging


def configure_logging() -> None:
    """Configure concise application logging without request or secret data."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
