"""Tax Vaapsi - Notice Defense Lambda Handler"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handler(event, context):
    try:
        user_id = event.get("user_id", "")
        notice_text = event.get("notice_text", "")
        portal = event.get("portal", "GST")
        business_facts = event.get("business_facts", {})
        from agents.notice_defense_agent import NoticeDefenseAgent
        agent = NoticeDefenseAgent()
        result = agent.full_defense_pipeline(user_id, notice_text, business_facts, portal)
        return {"statusCode": 200, "body": json.dumps(result, default=str)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
