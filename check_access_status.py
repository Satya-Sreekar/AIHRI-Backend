#!/usr/bin/env python3
"""
Comprehensive AWS Bedrock access status check
"""

import os
import json
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_all_regions():
    """Check access in different regions"""
    regions = ['us-east-1', 'us-west-2', 'ap-south-1', 'eu-west-1']
    models_to_test = [
        'amazon.titan-text-express-v1',
        'amazon.titan-tg1-large',
        'amazon.titan-text-lite-v1'
    ]
    
    print("🌍 Checking AWS Bedrock access across regions...")
    print("=" * 60)
    
    for region in regions:
        print(f"\n📍 Region: {region}")
        print("-" * 30)
        
        try:
            client = boto3.client(
                'bedrock-runtime',
                region_name=region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            for model_id in models_to_test:
                try:
                    request_body = {
                        "inputText": "Test",
                        "textGenerationConfig": {
                            "maxTokenCount": 10,
                            "temperature": 0.7
                        }
                    }
                    
                    response = client.invoke_model(
                        modelId=model_id,
                        body=json.dumps(request_body),
                        contentType="application/json"
                    )
                    
                    response_body = json.loads(response['body'].read())
                    generated_text = response_body.get('results', [{}])[0].get('outputText', '')
                    
                    print(f"✅ {model_id} - ACCESSIBLE")
                    print(f"   Response: {generated_text[:50]}...")
                    
                except Exception as e:
                    if "AccessDeniedException" in str(e):
                        print(f"❌ {model_id} - Access Denied")
                    else:
                        print(f"⚠️ {model_id} - {str(e)[:50]}...")
                        
        except Exception as e:
            print(f"❌ Region {region} - {str(e)[:50]}...")

def check_model_listing():
    """Check if we can list models in different regions"""
    regions = ['us-east-1', 'us-west-2', 'ap-south-1', 'eu-west-1']
    
    print("\n📋 Checking model availability across regions...")
    print("=" * 60)
    
    for region in regions:
        print(f"\n📍 Region: {region}")
        print("-" * 30)
        
        try:
            client = boto3.client(
                'bedrock',
                region_name=region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            response = client.list_foundation_models()
            
            # Filter for Titan models
            titan_models = []
            for model in response.get('modelSummaries', []):
                if 'titan' in model['modelId'].lower():
                    titan_models.append(model['modelId'])
            
            print(f"Found {len(titan_models)} Titan models:")
            for model in titan_models:
                print(f"  - {model}")
                
        except Exception as e:
            print(f"❌ Region {region} - {str(e)[:50]}...")

if __name__ == "__main__":
    print("🔍 AWS Bedrock Access Status Check")
    print("=" * 60)
    
    check_model_listing()
    check_all_regions()
    
    print("\n📝 Summary:")
    print("- If you see ✅ ACCESSIBLE, that model is ready to use")
    print("- If you see ❌ Access Denied, access is still propagating")
    print("- Access propagation can take 5-30 minutes")
    print("- Check your AWS Bedrock console for access status")

