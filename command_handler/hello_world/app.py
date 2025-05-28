import json
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEventV2,
    event_source,
)

logger = Logger(service="hello")

app = APIGatewayHttpResolver()


@app.post("/start")
def start():
    logger.info("start called")
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "start!",
            }
        ),
    }


@app.post("/stop")
def start():
    logger.info("stop called")
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "stop!",
            }
        ),
    }


@event_source(data_class=APIGatewayProxyEventV2)
def lambda_handler(event: APIGatewayProxyEventV2, context: LambdaContext):
    """Sample pure Lambda function

    Parameters
    ----------
    event: HTTP API Proxy Event
    context: Lambda Context runtime methods and attributes

    Returns
    ------
    HTTP API Proxy Response

    """

    logger.info(event)
    return app.resolve(event, context)
