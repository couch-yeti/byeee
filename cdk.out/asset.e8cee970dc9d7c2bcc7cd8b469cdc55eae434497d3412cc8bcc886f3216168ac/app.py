import os

import aws_cdk as cdk
from infra import stacks

from dotenv import load_dotenv

load_dotenv(".env.secret")

app = cdk.App()
stack = stacks.MainStack(scope=app, name="byeee")

tags = {
    "project-domain": "travel",
    "project-name": "byeee",
}

for tag, value in tags.items():
    cdk.Tags.of(stack).add(tag, value)

app.synth()
