import json
import os

import jwt

AUTH_DOMAIN = os.environ["AUTH_DOMAIN"]
API_IDENTIFIER = os.environ["API_IDENTIFIER"]  # ALSO Audience

ISSUER = f"https://{AUTH_DOMAIN}"


def build_policy(resource, principal_id: str, allow_or_not: bool = True):
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": allow_or_not,
                "Resource": resource,
            }
        ],
    }
    return {"principalId": principal_id, "policyDocument": policy}


def lambda_handler(event, context=None):
    try:
        token = event["authorizationToken"].split(" ")[1]
        decoded_token = jwt.decode(
            token,
            "public_key_here",
            algorithms=["RS256"],
            audience=API_IDENTIFIER,
            issuer=ISSUER,
        )
        method_arn = event["method_arn"]
        return build_policy(
            resource=method_arn, decoded_token=decoded_token, allow_or_not=True
        )

    except:
        return build_policy(resource=["*"], principal_id="fail_id", allow_or_not=False)
