import json
import os
import boto3
from datetime import datetime
from django.conf import settings
from botocore.exceptions import ClientError, NoCredentialsError


class BedrockService:
    """
    Service class for interacting with AWS Bedrock models
    """
    
    def __init__(self):
        self.region = settings.AWS_REGION
        self.api_key = settings.AWS_BEDROCK_API_KEY
        
        if not self.api_key:
            raise ValueError("AWS_Bedrock API key not found in environment variables")
        
        # Initialize Bedrock client
        try:
            # Check for separate AWS credentials first
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if access_key_id and secret_access_key:
                # Use separate credentials
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key
                )
            elif ':' in self.api_key:
                # API key contains both access key and secret key
                access_key, secret_key = self.api_key.split(':', 1)
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
            else:
                # Try using the API key as access key and look for secret in environment
                secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                if secret_key:
                    self.bedrock_client = boto3.client(
                        'bedrock-runtime',
                        region_name=self.region,
                        aws_access_key_id=self.api_key,
                        aws_secret_access_key=secret_key
                    )
                else:
                    # Try using default AWS credentials (from ~/.aws/credentials or environment)
                    self.bedrock_client = boto3.client(
                        'bedrock-runtime',
                        region_name=self.region
                    )
        except Exception as e:
            raise ValueError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def get_available_models(self):
        """
        Get list of available Bedrock models
        """
        try:
            # Create a separate client for listing models
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if access_key_id and secret_access_key:
                # Use separate credentials
                bedrock_client = boto3.client(
                    'bedrock',
                    region_name=self.region,
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key
                )
            elif ':' in self.api_key:
                access_key, secret_key = self.api_key.split(':', 1)
                bedrock_client = boto3.client(
                    'bedrock',
                    region_name=self.region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
            else:
                secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                if secret_key:
                    bedrock_client = boto3.client(
                        'bedrock',
                        region_name=self.region,
                        aws_access_key_id=self.api_key,
                        aws_secret_access_key=secret_key
                    )
                else:
                    bedrock_client = boto3.client(
                        'bedrock',
                        region_name=self.region
                    )
            
            # List foundation models
            response = bedrock_client.list_foundation_models()
            
            models = []
            for model in response.get('modelSummaries', []):
                if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                    models.append({
                        'name': model['modelId'],
                        'provider': model.get('providerName', 'Unknown'),
                        'input_modalities': model.get('inputModalities', []),
                        'output_modalities': model.get('outputModalities', []),
                    })
            
            return models
        except Exception as e:
            # Return default models if API call fails
            print(f"Warning: Could not fetch models from AWS Bedrock: {str(e)}")
            return [
                {
                    'name': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                    'provider': 'Anthropic',
                    'input_modalities': ['TEXT', 'IMAGE'],
                    'output_modalities': ['TEXT'],
                },
                {
                    'name': 'amazon.nova-pro-v1:0',
                    'provider': 'Amazon',
                    'input_modalities': ['TEXT', 'IMAGE', 'VIDEO'],
                    'output_modalities': ['TEXT'],
                },
                {
                    'name': 'openai.gpt-oss-120b-1:0',
                    'provider': 'OpenAI',
                    'input_modalities': ['TEXT'],
                    'output_modalities': ['TEXT'],
                },
                {
                    'name': 'meta.llama3-8b-instruct-v1:0',
                    'provider': 'Meta',
                    'input_modalities': ['TEXT'],
                    'output_modalities': ['TEXT'],
                },
            ]
    
    def generate_text(self, model_id, prompt, options=None, stream=True):
        """
        Generate text using AWS Bedrock model
        """
        if options is None:
            options = {}
        
        # Default parameters
        temperature = options.get('temperature', 0.7)
        max_tokens = options.get('max_tokens', 1000)
        top_p = options.get('top_p', 0.9)
        
        try:
            # Determine model provider and format request accordingly
            if 'anthropic.claude' in model_id:
                return self._generate_claude(model_id, prompt, temperature, max_tokens, top_p, stream)
            elif 'amazon.titan' in model_id:
                return self._generate_titan(model_id, prompt, temperature, max_tokens, top_p, stream)
            elif 'meta.llama' in model_id:
                return self._generate_llama(model_id, prompt, temperature, max_tokens, top_p, stream)
            else:
                # Default to Claude format
                return self._generate_claude(model_id, prompt, temperature, max_tokens, top_p, stream)
                
        except ClientError as e:
            # Handle specific AWS errors
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == "AccessDeniedException":
                return self._generate_fallback_response(model_id, prompt, stream)
            elif error_code == "ValidationException":
                # Treat unknown/invalid model the same as access issues — fall back to demo
                return self._generate_fallback_response(model_id, prompt, stream)
            else:
                raise Exception(f"AWS Bedrock error ({error_code}): {error_message}")
        except Exception as e:
            # Provide a fallback response when AWS is not available
            if ("Unable to locate credentials" in str(e) or 
                "InvalidAccessKeyId" in str(e) or 
                "AccessDeniedException" in str(e)):
                return self._generate_fallback_response(model_id, prompt, stream)
            raise Exception(f"Generation error: {str(e)}")
    
    def _generate_claude(self, model_id, prompt, temperature, max_tokens, top_p, stream):
        """
        Generate text using Claude models
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if stream:
            request_body["stream"] = True
        
        response = self.bedrock_client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        if stream:
            return self._process_streaming_response(response, model_id)
        else:
            return self._process_non_streaming_response(response, model_id)
    
    def _generate_titan(self, model_id, prompt, temperature, max_tokens, top_p, stream):
        """
        Generate text using Amazon Titan models
        """
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": top_p
            }
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        return self._process_titan_response(response, model_id)
    
    def _generate_llama(self, model_id, prompt, temperature, max_tokens, top_p, stream):
        """
        Generate text using Meta Llama models
        """
        # Bedrock now supports the dedicated `converse` API for Llama-3 models.
        # Build the parameters to match the CLI example that works in ap-south-1.

        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]

        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p,
        }

        # NOTE: Streaming via `converse` currently returns the full output at once,
        # so we manually wrap it in a generator when the caller requests streaming.

        response = self.bedrock_client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inference_config,
        )

        if stream:
            def generate_stream():
                output_text = (
                    response.get("output", {})
                    .get("message", {})
                    .get("content", [{}])[0]
                    .get("text", "")
                )

                # Yield the entire response in a single chunk for now
                yield {
                    "model": model_id,
                    "created_at": datetime.now().isoformat(),
                    "response": output_text,
                    "done": True,
                    "usage": response.get("usage", {}),
                    "stop_reason": response.get("stopReason", "end_turn"),
                }

            return generate_stream()

        # Non-streaming – return immediately
        return {
            "model": model_id,
            "created_at": datetime.now().isoformat(),
            "response": (
                response.get("output", {})
                .get("message", {})
                .get("content", [{}])[0]
                .get("text", "")
            ),
            "done": True,
            "usage": response.get("usage", {}),
            "stop_reason": response.get("stopReason", "end_turn"),
        }
    
    def _process_streaming_response(self, response, model_id):
        """
        Process streaming response from Claude models
        """
        def generate_stream():
            try:
                for event in response['body']:
                    chunk = json.loads(event['chunk']['bytes'])
                    
                    if chunk['type'] == 'content_block_delta':
                        content = chunk['delta']['text']
                        yield {
                            'model': model_id,
                            'created_at': datetime.now().isoformat(),
                            'response': content,
                            'done': False
                        }
                    elif chunk['type'] == 'message_stop':
                        yield {
                            'model': model_id,
                            'created_at': datetime.now().isoformat(),
                            'response': '',
                            'done': True,
                            'usage': chunk.get('usage', {}),
                            'stop_reason': chunk.get('stop_reason', 'end_turn')
                        }
                        break
                        
            except Exception as e:
                yield {
                    'model': model_id,
                    'created_at': datetime.now().isoformat(),
                    'response': '',
                    'done': True,
                    'error': str(e)
                }
        
        return generate_stream()
    
    def _process_non_streaming_response(self, response, model_id):
        """
        Process non-streaming response
        """
        response_body = json.loads(response['body'].read())
        
        return {
            'model': model_id,
            'created_at': datetime.now().isoformat(),
            'response': response_body.get('content', [{}])[0].get('text', ''),
            'done': True,
            'usage': response_body.get('usage', {}),
            'stop_reason': response_body.get('stop_reason', 'end_turn')
        }
    
    def _process_titan_response(self, response, model_id):
        """
        Process Amazon Titan response
        """
        response_body = json.loads(response['body'].read())
        
        return {
            'model': model_id,
            'created_at': datetime.now().isoformat(),
            'response': response_body.get('results', [{}])[0].get('outputText', ''),
            'done': True,
            'usage': response_body.get('usage', {})
        }
    
    def _process_llama_response(self, response, model_id):
        """
        Process Meta Llama response
        """
        response_body = json.loads(response['body'].read())
        
        return {
            'model': model_id,
            'created_at': datetime.now().isoformat(),
            'response': response_body.get('generation', ''),
            'done': True,
            'usage': response_body.get('usage', {})
        }
    
    def _process_llama_streaming_response(self, response, model_id):
        """
        Process streaming response from Meta Llama models
        """
        def generate_stream():
            try:
                for event in response["body"]:
                    chunk = json.loads(event["chunk"]["bytes"])

                    # Llama streaming responses typically include a "generation" field
                    if "generation" in chunk:
                        yield {
                            "model": model_id,
                            "created_at": datetime.now().isoformat(),
                            "response": chunk["generation"],
                            "done": False
                        }

                    # Detect stop condition – Bedrock marks the final message with "is_end": true
                    if chunk.get("is_end", False):
                        yield {
                            "model": model_id,
                            "created_at": datetime.now().isoformat(),
                            "response": "",
                            "done": True,
                            "usage": chunk.get("usage", {}),
                            "stop_reason": chunk.get("stop_reason", "end_turn")
                        }
                        break
            except Exception as e:
                yield {
                    "model": model_id,
                    "created_at": datetime.now().isoformat(),
                    "response": "",
                    "done": True,
                    "error": str(e)
                }

        return generate_stream()
    
    def _generate_fallback_response(self, model_id, prompt, stream):
        """
        Generate a fallback response when AWS Bedrock is not available
        """
        fallback_response = f"I'm sorry, but I'm currently unable to connect to AWS Bedrock. This appears to be a demo response. Your prompt was: '{prompt[:100]}...' Please check your AWS credentials configuration."
        
        if stream:
            def generate_fallback_stream():
                yield {
                    'model': model_id,
                    'created_at': datetime.now().isoformat(),
                    'response': fallback_response,
                    'done': True,
                    'usage': {'input_tokens': len(prompt.split()), 'output_tokens': len(fallback_response.split())},
                    'stop_reason': 'demo_mode'
                }
            return generate_fallback_stream()
        else:
            return {
                'model': model_id,
                'created_at': datetime.now().isoformat(),
                'response': fallback_response,
                'done': True,
                'usage': {'input_tokens': len(prompt.split()), 'output_tokens': len(fallback_response.split())},
                'stop_reason': 'demo_mode'
            }
