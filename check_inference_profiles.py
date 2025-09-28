#!/usr/bin/env python3
"""
Check available AWS Bedrock inference profiles
"""

import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_inference_profiles():
    """Check what inference profiles are available"""
    try:
        # Initialize Bedrock client
        client = boto3.client(
            'bedrock',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # List foundation models
        response = client.list_foundation_models()
        
        # Filter for models that support on-demand
        on_demand_models = []
        for model in response.get('modelSummaries', []):
            if ('TEXT' in model.get('outputModalities', []) and 
                model.get('modelLifecycle', {}).get('status') == 'ACTIVE'):
                
                # Check if it supports on-demand
                inference_types = model.get('inferenceTypesSupported', [])
                if 'ON_DEMAND' in inference_types:
                    on_demand_models.append(model)
        
        print(f"Found {len(on_demand_models)} models supporting on-demand inference:")
        print("=" * 60)
        
        for i, model in enumerate(on_demand_models[:20], 1):  # Show first 20
            print(f"{i:2d}. {model['modelId']}")
            print(f"    Provider: {model.get('providerName', 'Unknown')}")
            print(f"    Inference Types: {model.get('inferenceTypesSupported', [])}")
            print(f"    Input: {model.get('inputModalities', [])}")
            print(f"    Output: {model.get('outputModalities', [])}")
            print()
        
        if len(on_demand_models) > 20:
            print(f"... and {len(on_demand_models) - 20} more models")
        
        return on_demand_models
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

if __name__ == "__main__":
    models = check_inference_profiles()

