from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from common.log import logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@logger.inject_lambda_context(log_event=True, clear_state=True)
def lambda_handler(event, context=None):
    handler = Mangum(app)
    return handler(event, context)
