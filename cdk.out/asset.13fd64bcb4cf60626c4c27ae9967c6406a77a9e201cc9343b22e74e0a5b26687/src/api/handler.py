from mangum import Mangum

from common.log import logger
from application import app, ExceptionLoggingMiddleware


# app.add_middleware(ExceptionLoggingMiddleware)
# app.include_router(trips.router)
# app.include_router(itinerary.router)


@logger.inject_lambda_context(log_event=True, clear_state=True)
def lambda_handler(event, context=None):
    handler = Mangum(app)
    return handler(event, context)


if __name__ == "__main__":
    import uvicorn, os

    os.environ["TABLE"] = "byeee-dev"

    uvicorn.run("handler:app", host="0.0.0.0", port=8000, reload=True)
