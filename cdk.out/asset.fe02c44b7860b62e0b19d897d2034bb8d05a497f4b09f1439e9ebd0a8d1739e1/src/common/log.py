import os

from aws_lambda_powertools import Logger

log_service = "bye_app"
logger = Logger(service=log_service, level=os.getenv("LEVEL", "WARN"))


def get_child_logger() -> Logger:
    return Logger(service=log_service, child=True)
