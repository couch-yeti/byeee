from pathlib import Path
import os

import aws_cdk as cdk
from aws_cdk import aws_lambda
from aws_cdk.aws_ecr_assets import DockerImageAsset


def get_project_root():
    path = Path(os.path.dirname(__file__)).resolve()
    while True:
        if "pyproject.toml" in os.listdir(path):
            return path
        if path == Path("/"):
            break
        path = path.parent
    return None


def get_lambda_asset(path: str) -> aws_lambda.Code:
    """Get the lambda asset"""

    _path = str((get_project_root() / path).resolve())
    return aws_lambda.Code.from_asset(
        path=str(_path),
        bundling=cdk.BundlingOptions(
            image=aws_lambda.Runtime.PYTHON_3_11.bundling_image,
            command=[
                "bash",
                "-c",
                "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
            ],
        ),
    )
