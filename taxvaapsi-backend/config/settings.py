"""
Tax Vaapsi - Application Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Tax Vaapsi"
    APP_VERSION: str = "3.0.0"
    APP_ENV: str = "development"
    SECRET_KEY: str = "taxvaapsi-secret-key-change-in-production-min-32"

    # AWS Core
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: str = "ap-south-1"

    # AWS Bedrock
    BEDROCK_MODEL_ID: str = "amazon.nova-pro-v1:0"
    BEDROCK_REGION: str = "ap-south-1"

    # Bedrock Agent IDs (set after agent creation)
    BEDROCK_GST_AGENT_ID: str = ""
    BEDROCK_GST_AGENT_ALIAS_ID: str = ""
    BEDROCK_IT_AGENT_ID: str = ""
    BEDROCK_IT_AGENT_ALIAS_ID: str = ""
    BEDROCK_NOTICE_AGENT_ID: str = ""
    BEDROCK_NOTICE_AGENT_ALIAS_ID: str = ""
    BEDROCK_SUPERVISOR_AGENT_ID: str = ""
    BEDROCK_SUPERVISOR_AGENT_ALIAS_ID: str = ""

    # AWS DynamoDB
    DYNAMODB_TABLE_PREFIX: str = "taxvaapsi_"
    DYNAMODB_ENDPOINT_URL: str = "http://localhost:8000"
    USE_LOCAL_DYNAMODB: bool = True

    # AWS S3
    S3_BUCKET_NAME: str = "taxvaapsi-documents-local"
    S3_REGION: str = "ap-south-1"

    # AWS SQS
    SQS_GST_QUEUE_URL: str = ""
    SQS_IT_QUEUE_URL: str = ""
    SQS_NOTICE_QUEUE_URL: str = ""

    # AWS Step Functions
    SFN_GST_WORKFLOW_ARN: str = ""
    SFN_IT_WORKFLOW_ARN: str = ""
    SFN_NOTICE_WORKFLOW_ARN: str = ""

    # AWS Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""

    # AWS SNS
    SNS_TOPIC_ARN: str = ""

    # MCP Servers
    MCP_GST_SERVER_PORT: int = 9101
    MCP_IT_SERVER_PORT: int = 9102
    MCP_TAX_LAW_SERVER_PORT: int = 9103

    # Dummy Portals
    GST_PORTAL_URL: str = "http://localhost:8001"
    IT_PORTAL_URL: str = "http://localhost:8002"
    USE_MOCK_PORTALS: bool = True

    # A2A Protocol
    A2A_AGENT_CARD_URL: str = "http://localhost:8081/.well-known/agent.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
