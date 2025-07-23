from config import ROOT_DIR
import logging
import os.path


def module_logger(module_name: str):
    name_file = "_".join(module_name.split("."))
    log_path = os.path.join(ROOT_DIR, f"log/{name_file}.log")
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s %(module)s %(funcName)s %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    return logger
