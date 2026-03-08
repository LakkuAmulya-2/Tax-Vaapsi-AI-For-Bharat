"""
Quick test script to verify Bedrock model access
"""
import json
import boto3
from config.settings import get_settings

settings = get_settings()

def test_model(model_id):
    """Test if a model is accessible"""
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    body = {
        "messages": [{"role": "user", "content": [{"text": "Say OK"}]}],
        "inferenceConfig": {"maxTokens": 50, "temperature": 0.1}
    }
    
    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        resp_body = json.loads(response["body"].read())
        text = resp_body["output"]["message"]["content"][0]["text"]
        print(f"✅ {model_id}: {text}")
        return True
    except Exception as e:
        print(f"❌ {model_id}: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing AWS Bedrock Model Access")
    print("="*60 + "\n")
    
    models_to_test = [
        "amazon.nova-pro-v1:0",
        "amazon.nova-lite-v1:0",
        "amazon.nova-micro-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-haiku-20241022-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
    ]
    
    working_models = []
    for model in models_to_test:
        if test_model(model):
            working_models.append(model)
    
    print("\n" + "="*60)
    print(f"Working Models: {len(working_models)}/{len(models_to_test)}")
    print("="*60)
    
    if working_models:
        print("\n✅ Recommended model to use:")
        print(f"   {working_models[0]}")
    else:
        print("\n⚠️  No models accessible. Please enable model access in AWS Bedrock console:")
        print("   https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess")
