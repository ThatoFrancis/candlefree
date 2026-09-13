"""Scheduled trigger — invokes the CandleFree AgentCore runtime for one background pass."""

import json
import os
import uuid

import boto3

client = boto3.client("bedrock-agentcore", region_name=os.environ["AGENT_REGION"])


def handler(event, context):
    response = client.invoke_agent_runtime(
        agentRuntimeArn=os.environ["AGENT_RUNTIME_ARN"],
        runtimeSessionId=f"candlefree-scheduled-{uuid.uuid4()}",
        payload=json.dumps({"prompt": ""}),  # empty -> agent uses its background prompt
    )
    body = response["response"].read().decode("utf-8", errors="replace")
    print(f"CandleFree scheduled pass complete: {body[:2000]}")
    return {"statusCode": 200}
