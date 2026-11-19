# ruff: noqa: E402  (imports follow load_dotenv so env is set first)
from dotenv import load_dotenv

load_dotenv()

from logging_setup import setup_logging

setup_logging()
