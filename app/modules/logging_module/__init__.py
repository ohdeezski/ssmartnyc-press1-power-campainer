import logging
import os


def setup_logging(app=None):
    log_level = "INFO"
    if app and hasattr(app, "config"):
        log_level = app.config.get("LOG_LEVEL", "INFO")
    log_level_val = getattr(logging, log_level, logging.INFO)

    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
    )
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger("street_smart")
    root_logger.setLevel(log_level_val)

    if not root_logger.handlers:
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setLevel(log_level_val)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level_val)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    return root_logger


logger = setup_logging()
