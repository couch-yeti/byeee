import os

import aws_cdk as cdk
from aws_cdk import aws_apigateway, aws_iam

from infra.components import Func


class ApiStack(cdk.NestedStack):
    def __init__(self, scope, cid):
        super().__init__(scope=scope, id=cid)
        self.create_lambda_functions()
        self.create_rest_gateway()

    def create_lambda_functions(self):
        """Function creates a proxy lambda and an auth lambda for the Rest API"""

        self.api_lambda = Func(scope=self, cid="proxy", path="src/api")
        self.auth_lambda = Func(scope=self, cid="auth", path="src/auth")

    def create_rest_gateway(self):
        """Creates the API Gateway with permissions and authorizer and associates the gateway with the
        lambdas
        """
        auth_policy_statements = [
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction",
                    "lambda:GetFunction",
                    "lambda:ListFunctions",
                ],
                effect=aws_iam.Effect.ALLOW,
                resources=[
                    self.api_lambda.function.function_arn,
                    self.auth_lambda.function.function_arn,
                ],
            ),
        ]

        auth_role = aws_iam.Role(
            self,
            "auth-role",
            assumed_by=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            inline_policies={
                "auth-polices": aws_iam.PolicyDocument(
                    statements=auth_policy_statements
                )
            },
        )

        authorizer = aws_apigateway.RequestAuthorizer(
            scope=self,
            id="authorizer",
            handler=self.auth_lambda.function,
            assume_role=auth_role,
            identity_sources=[
                aws_apigateway.IdentitySource.header("authorizationToken")
            ],
        )

        self.gateway = aws_apigateway.RestApi(
            scope=self,
            id="gateway",
            deploy=True,
            deploy_options=aws_apigateway.StageOptions(
                stage_name=os.environ["ENVIRONMENT"]
            ),
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=["*"]
            ),
        )

        self.auth_resource = self.gateway.root.add_resource(
            path_part="auth",
            default_method_options=aws_apigateway.MethodOptions(
                authorizer=None,
                authorization_type=aws_apigateway.AuthorizationType.NONE,
            ),
        )
        self.auth_resource.add_proxy(
            default_integration=aws_apigateway.LambdaIntegration(
                self.api_lambda.function
            )
        )

        self.api_swagger_resource = self.gateway.root.add_resource(
            "swagger",
            default_integration=aws_apigateway.LambdaIntegration(
                self.api_lambda.function
            ),
        )
        self.api_swagger_proxy = self.api_swagger_resource.add_resource("{doctype}")
        self.api_swagger_method = self.api_swagger_proxy.add_method(
            "GET", method_responses=[aws_apigateway.MethodResponse(status_code="200")]
        )

        self.gateway.root.add_proxy(
            default_integration=aws_apigateway.LambdaIntegration(
                self.api_lambda.function
            ),
            any_method=True,
            default_method_options=aws_apigateway.MethodOptions(authorizer=authorizer),
        )


class MainStack(cdk.Stack):

    def __init__(self, scope, name):
        super().__init__(scope=scope, id=name)

        self.api_stack = ApiStack(scope=self, cid="api")