"""Tax Vaapsi - IT Tracker Lambda Handler"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handler(event, context):
    try:
        user_id = event.get("user_id", "")
        pan = event.get("pan", "")
        from agents.income_tax_agent import IncomeTaxAgent
        agent = IncomeTaxAgent()
        result = agent.scan_it_opportunities(user_id, pan)
        return {"statusCode": 200, "body": json.dumps(result, default=str)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
