import os
from typing import Optional, Dict

import aws_cdk as cdk
from aws_cdk import aws_dynamodb, aws_lambda
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct

from infra.utils import get_lambda_asset


class Func(Construct):
    def __init__(
        self,
        scope: Construct,
        cid: str,
        path: str,
        environment: Dict[str, str] = None,
        memory_size: int = 528,
        duration: cdk.Duration = cdk.Duration.seconds(amount=60),
        **kw,
    ):
        self.name = cid
        self.path = path
        self.environment = environment or {}
        super().__init__(scope=scope, id=cid, **kw)
        self.docker_image = self._create_image()
        self.function = aws_lambda.DockerImageFunction(
            scope=self,
            id=cid,
            code=aws_lambda.DockerImageCode.from_ecr(
                repository=self.docker_image.repository,
                tag_or_digest=self.docker_image.asset_hash,
            ),
            memory_size=memory_size,
            duration=duration,
            environment=environment,
        )

    def _create_image(self):
        """function assumes both the app.py file and the Dockerfile are at root"""

        docker_image = DockerImageAsset(
            scope=self,
            id=f"{self.name}-image",
            directory=os.getcwd(),
            # build_args={"FUNCTION_DIR": self.path},
        )
        return docker_image


class Table(Construct):
    def __init__(
        self,
        scope: Construct,
        cid: str,
        pk: str,
        sk: Optional[str] = None,
        **kw,
    ):
        super().__init__(scope=scope, id=cid, **kw)
        self.pk = self.attribute(name=pk)
        self.sk = self.attribute(name=sk)

        self.table = aws_dynamodb.Table(
            scope=self,
            id="table",
            partition_key=self.pk,
            sort_key=self.sk,
            time_to_live_attribute="expiration",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )

    def attribute(self, name: Optional[str] = None) -> aws_dynamodb.Attribute:
        if not name:
            return None
        return aws_dynamodb.Attribute(name=name, type=aws_dynamodb.AttributeType.STRING)

    def add_gsi(self, gsi_name: str, pk: str, sk: Optional[str] = None) -> None:
        """Function adds a GSI to an existing table"""
        gsi_pk = self.attribute(name=pk)
        gsi_sk = self.attribute(name=sk)

        self.table.add_global_secondary_index(
            index_name=gsi_name, partition_key=gsi_pk, sort_key=gsi_sk
        )

    def add_lsi(self, lsi_name: str, sort_key: str):
        lsi_sk = self.attribute(name=sort_key)
        self.table.add_local_secondary_index(sort_key=lsi_sk, index_name=lsi_name)
