#!/usr/bin/env python3
"""
Wait for AWS Bedrock model access to propagate
"""

import os
import json
import boto3
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_access():
    """Check if Titan model access is available"""
    try:
        client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        model_id = "amazon.titan-tg1-large"
        
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
        
        print(f"✅ SUCCESS! Access granted to {model_id}")
        print(f"📄 Response: {generated_text}")
        return True
        
    except Exception as e:
        if "AccessDeniedException" in str(e):
            print(f"⏳ Access not yet available: {str(e)[:100]}...")
            return False
        else:
            print(f"❌ Other error: {str(e)}")
            return False

def main():
    """Wait for access with periodic checks"""
    print("🚀 Waiting for Amazon Titan Text G1 - Express access...")
    print("=" * 60)
    
    max_attempts = 20  # Check for up to 10 minutes
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\nAttempt {attempt}/{max_attempts}:")
        
        if check_access():
            print("\n🎉 Access is now available!")
            print("You can now use the Titan Text G1 - Express model.")
            break
        else:
            if attempt < max_attempts:
                print("⏳ Waiting 30 seconds before next check...")
                time.sleep(30)
            else:
                print("\n⚠️ Access not available after maximum attempts.")
                print("This might take longer to propagate or there might be an issue.")
                print("Please check your AWS Bedrock console for access status.")

if __name__ == "__main__":
    main()

