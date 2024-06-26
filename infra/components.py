import os
from typing import Optional, Dict

import aws_cdk as cdk
from aws_cdk import aws_dynamodb, aws_lambda, aws_ecr_assets, aws_ecr
from constructs import Construct


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
        super().__init__(scope=scope, id=cid, **kw)
        self.name = cid
        self.path = path
        self.environment = environment or {}
        self.repo = self._get_repo()
        self.function = aws_lambda.DockerImageFunction(
            scope=self,
            id=cid,
            code=aws_lambda.DockerImageCode.from_ecr(
                repository=self.repo,
                cmd=[self.path],
                tag_or_digest="1.0.3",
            ),
            memory_size=memory_size,
            timeout=duration,
            environment=environment,
        )

    def _get_repo(self):

        return aws_ecr.Repository.from_repository_arn(
            scope=self,
            id="repo",
            repository_arn="arn:aws:ecr:us-west-2:911808035826:repository/byeee-repo",
        )


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
        return aws_dynamodb.Attribute(
            name=name, type=aws_dynamodb.AttributeType.STRING
        )

    def add_gsi(
        self, gsi_name: str, pk: str, sk: Optional[str] = None
    ) -> None:
        """Function adds a GSI to an existing table"""
        gsi_pk = self.attribute(name=pk)
        gsi_sk = self.attribute(name=sk)

        self.table.add_global_secondary_index(
            index_name=gsi_name, partition_key=gsi_pk, sort_key=gsi_sk
        )

    def add_lsi(self, lsi_name: str, sort_key: str):
        lsi_sk = self.attribute(name=sort_key)
        self.table.add_local_secondary_index(
            sort_key=lsi_sk, index_name=lsi_name
        )
