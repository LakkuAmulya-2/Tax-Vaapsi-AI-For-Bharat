"""
Tax Vaapsi - DynamoDB Table Setup Script
Creates all required DynamoDB tables (local or AWS)
Run once: python dynamodb/setup_tables.py
"""
import boto3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings

settings = get_settings()
PREFIX = settings.DYNAMODB_TABLE_PREFIX

def get_client():
    kwargs = {"region_name": settings.AWS_DEFAULT_REGION}
    if settings.USE_LOCAL_DYNAMODB:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.client("dynamodb", **kwargs)


TABLES = [
    {
        "TableName": f"{PREFIX}users",
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}gst_scans",
        "KeySchema": [{"AttributeName": "scan_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "scan_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}it_refunds",
        "KeySchema": [{"AttributeName": "refund_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "refund_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}tds_records",
        "KeySchema": [{"AttributeName": "tds_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "tds_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}notices",
        "KeySchema": [{"AttributeName": "notice_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "notice_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}compliance_events",
        "KeySchema": [{"AttributeName": "event_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "event_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}agent_activity",
        "KeySchema": [{"AttributeName": "activity_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "activity_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        "BillingMode": "PAY_PER_REQUEST",
    },
]


def create_tables():
    client = get_client()
    print(f"\n{'='*60}")
    print(f"Tax Vaapsi - DynamoDB Table Setup")
    print(f"Region: {settings.AWS_DEFAULT_REGION}")
    print(f"Local: {settings.USE_LOCAL_DYNAMODB}")
    print(f"{'='*60}\n")

    for table_def in TABLES:
        table_name = table_def["TableName"]
        try:
            client.create_table(**table_def)
            print(f"✅ Created: {table_name}")
        except client.exceptions.ResourceInUseException:
            print(f"⚠️  Already exists: {table_name}")
        except Exception as e:
            print(f"❌ Failed: {table_name} - {e}")

    print(f"\n✅ DynamoDB setup complete! {len(TABLES)} tables ready.")
    print("\nFor local testing, ensure DynamoDB Local is running:")
    print("  docker run -p 8000:8000 amazon/dynamodb-local")


if __name__ == "__main__":
    create_tables()
