"""
Tax Vaapsi - AWS Configuration
All AWS clients initialized here - Only AWS services used
Region: ap-south-1 (Mumbai)
"""
import boto3
from botocore.config import Config
from config.settings import get_settings

settings = get_settings()

RETRY_CONFIG = Config(
    region_name=settings.AWS_DEFAULT_REGION,
    retries={"max_attempts": 3, "mode": "adaptive"},
    connect_timeout=10,
    read_timeout=60,
)


def get_bedrock_client():
    """AWS Bedrock Runtime - Nova Pro for all AI inference"""
    return boto3.client("bedrock-runtime", region_name=settings.BEDROCK_REGION, config=RETRY_CONFIG)


def get_bedrock_agent_client():
    """AWS Bedrock Agent Runtime - invoke native Bedrock agents"""
    return boto3.client("bedrock-agent-runtime", region_name=settings.BEDROCK_REGION, config=RETRY_CONFIG)


def get_bedrock_management_client():
    """AWS Bedrock Agent Management - create/manage agents"""
    return boto3.client("bedrock-agent", region_name=settings.BEDROCK_REGION, config=RETRY_CONFIG)


def get_dynamodb_resource():
    """AWS DynamoDB - Main database"""
    kwargs = {"region_name": settings.AWS_DEFAULT_REGION, "config": RETRY_CONFIG}
    if settings.USE_LOCAL_DYNAMODB:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_client():
    kwargs = {"region_name": settings.AWS_DEFAULT_REGION, "config": RETRY_CONFIG}
    if settings.USE_LOCAL_DYNAMODB:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.client("dynamodb", **kwargs)


def get_s3_client():
    """AWS S3 - Document storage"""
    return boto3.client("s3", region_name=settings.S3_REGION, config=RETRY_CONFIG)


def get_sqs_client():
    """AWS SQS - Async job queuing"""
    return boto3.client("sqs", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_step_functions_client():
    """AWS Step Functions - Workflow orchestration"""
    return boto3.client("stepfunctions", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_textract_client():
    """AWS Textract - OCR for invoices and notices"""
    return boto3.client("textract", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_comprehend_client():
    """AWS Comprehend - NLP for notice analysis"""
    return boto3.client("comprehend", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_rekognition_client():
    """AWS Rekognition - Signature verification"""
    return boto3.client("rekognition", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_sns_client():
    """AWS SNS - WhatsApp/SMS alerts"""
    return boto3.client("sns", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_secrets_manager_client():
    """AWS Secrets Manager - GST/PAN credentials"""
    return boto3.client("secretsmanager", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_kms_client():
    """AWS KMS - Encrypt PAN, GSTIN, bank details"""
    return boto3.client("kms", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_cognito_client():
    """AWS Cognito - User authentication"""
    return boto3.client("cognito-idp", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_cloudwatch_client():
    """AWS CloudWatch - Monitoring and metrics"""
    return boto3.client("cloudwatch", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_eventbridge_client():
    """AWS EventBridge - Event-driven tax deadline workflows"""
    return boto3.client("events", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)


def get_lambda_client():
    """AWS Lambda - Serverless function handlers"""
    return boto3.client("lambda", region_name=settings.AWS_DEFAULT_REGION, config=RETRY_CONFIG)
