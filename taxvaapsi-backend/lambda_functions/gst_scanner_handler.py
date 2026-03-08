"""
Tax Vaapsi - Lambda Handler: GST Scanner
Deployed as AWS Lambda function
Triggered by: Step Functions, SQS, Direct API calls
Runtime: Python 3.12
"""
import json
import os
import sys

# Add parent to path for Lambda layer compatibility
sys.path.insert(0, "/opt/python")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def handler(event, context):
    """
    AWS Lambda Handler - GST Scanner
    Scans 36 months of GST data for 7 refund types
    Powered by AWS Bedrock Nova Pro
    """
    try:
        # Parse input
        user_id = event.get("user_id", "")
        gstin = event.get("gstin", "")
        months = event.get("months", 36)

        if not gstin:
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "error": "GSTIN required"}),
            }

        # Import here to avoid cold start issues
        from agents.gst_refund_agent import GSTRefundAgent
        from services.dynamodb_service import DynamoDBService

        agent = GSTRefundAgent()
        result = agent.scan_and_detect(user_id, gstin)

        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str),
            "success": True,
            "total_recoverable": result.get("total_recoverable", 0),
            "refunds_found": result.get("refunds_found", 0),
        }

    except Exception as e:
        print(f"Lambda Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)}),
        }


def monitor_handler(event, context):
    """
    24/7 Monitoring Lambda - triggered by EventBridge every 24 hours
    Checks refund status and sends WhatsApp alerts
    """
    try:
        # Process SQS messages
        records = event.get("Records", [])
        results = []

        for record in records:
            body = json.loads(record.get("body", "{}"))
            user_id = body.get("user_id", "")
            entity_id = body.get("entity_id", "")
            job_type = body.get("job_type", "")

            if job_type == "GST_MONITOR":
                from agents.gst_refund_agent import GSTRefundAgent
                agent = GSTRefundAgent()
                status = agent.monitor_refund_status(user_id, entity_id)
                results.append(status)

        return {
            "statusCode": 200,
            "processed": len(results),
            "results": results,
        }

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}
