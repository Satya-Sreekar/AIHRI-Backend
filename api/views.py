import json
import requests
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .bedrock_service import BedrockService
from .serializers import BedrockRequestSerializer, BedrockResponseSerializer, OllamaRequestSerializer, OllamaResponseSerializer, TTSRequestSerializer


@extend_schema(
    tags=['AWS Bedrock'],
    summary='Generate text with AWS Bedrock model',
    description='Send a prompt to an AWS Bedrock model and get a streaming response',
    request=BedrockRequestSerializer,
    responses={
        200: BedrockResponseSerializer,
        400: None,
        500: None,
    },
    examples=[
        OpenApiExample(
            'Basic Request',
            value={
                'model': 'meta.llama3-8b-instruct-v1:0',
                'prompt': 'What is the capital of France?',
                'stream': True,
                'options': {'temperature': 0.7, 'max_tokens': 1000}
            },
            request_only=True,
        ),
        OpenApiExample(
            'Response',
            value={
                'model': 'meta.llama3-8b-instruct-v1:0',
                'created_at': '2024-01-01T00:00:00Z',
                'response': 'The capital of France is Paris.',
                'done': True,
                'usage': {'input_tokens': 10, 'output_tokens': 5},
                'stop_reason': 'end_turn'
            },
            response_only=True,
        ),
    ],
)
@api_view(['POST'])
@parser_classes([JSONParser])
def generate_text(request):
    """
    Generate text using an AWS Bedrock model with streaming support.
    
    This endpoint sends a request to the AWS Bedrock API and streams the response back
    to the client. The response is streamed as Server-Sent Events (SSE) format.
    """
    serializer = BedrockRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    try:
        # Initialize Bedrock service
        bedrock_service = BedrockService()
        
        # Generate text using Bedrock
        if data.get('stream', True):
            # Streaming response
            stream_generator = bedrock_service.generate_text(
                model_id=data['model'],
                prompt=data['prompt'],
                options=data.get('options', {}),
                stream=True
            )
            
            def generate_stream():
                """Generator function to stream the response"""
                try:
                    for chunk in stream_generator:
                        # Convert to SSE format
                        sse_data = f"data: {json.dumps(chunk)}\n\n"
                        yield sse_data.encode('utf-8')
                        
                        # If this is the final response, break
                        if chunk.get('done', False):
                            break
                except Exception as e:
                    error_data = f"data: {json.dumps({'error': str(e)})}\n\n"
                    yield error_data.encode('utf-8')
            
            # Return streaming response
            return StreamingHttpResponse(
                generate_stream(),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                }
            )
        else:
            # Non-streaming response
            response_data = bedrock_service.generate_text(
                model_id=data['model'],
                prompt=data['prompt'],
                options=data.get('options', {}),
                stream=False
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': f'Configuration error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['AWS Bedrock'],
    summary='List available models',
    description='Get a list of available AWS Bedrock models',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'models': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'provider': {'type': 'string'},
                            'input_modalities': {'type': 'array'},
                            'output_modalities': {'type': 'array'},
                        }
                    }
                }
            }
        },
        500: None,
    },
)
@api_view(['GET'])
def list_models(request):
    """
    Get a list of available AWS Bedrock models.
    """
    try:
        # Initialize Bedrock service
        bedrock_service = BedrockService()
        
        # Get available models
        models = bedrock_service.get_available_models()
        
        return Response({'models': models}, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': f'Configuration error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 


@csrf_exempt
def text_to_speech(request):
    """
    Convert text to speech using gTTS (Google Text-to-Speech) with streaming support.
    
    This endpoint converts text to speech using Google's TTS service and streams 
    the audio response back to the client.
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    # Handle GET request for testing
    if request.method == 'GET':
        # Default test parameters for GET request
        data = {
            'text': request.GET.get('text', 'Hello, this is a test of the text to speech system.'),
            'lang': request.GET.get('lang', 'en'),
            'tld': request.GET.get('tld', 'com'),
            'slow': request.GET.get('slow', 'false').lower() == 'true'
        }
    else:
        # Handle POST request with JSON data
        try:
            import json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                return JsonResponse(
                    {'error': 'Content-Type must be application/json'},
                    status=400
                )
            
            # Validate required fields
            required_fields = ['text', 'lang', 'tld', 'slow']
            for field in required_fields:
                if field not in data:
                    return JsonResponse(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON data'},
                status=400
            )
    
    # Import gTTS here to avoid import errors if not installed
    try:
        from gtts import gTTS
        import io
        import tempfile
        import os
    except ImportError:
        return JsonResponse(
            {'error': 'gTTS library not installed. Please install with: pip install gtts'},
            status=500
        )
    
    try:
        # Validate text input
        text = data['text'].strip()
        if not text:
            return JsonResponse(
                {'error': 'Text cannot be empty'},
                status=400
            )
        
        # Create gTTS object
        tts = gTTS(
            text=text,
            lang=data['lang'],
            tld=data['tld'],
            slow=data['slow']
        )
        
        # Use BytesIO to avoid file system issues
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Get the audio data
        audio_data = audio_buffer.getvalue()
        audio_buffer.close()
        
        if not audio_data:
            return JsonResponse(
                {'error': 'Failed to generate audio data'},
                status=500
            )
        
        # Stream the audio response
        def generate_audio_stream():
            """Generator function to stream the audio response"""
            try:
                # Stream the audio data in chunks
                chunk_size = 8192
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    if chunk:
                        yield chunk
            except Exception as e:
                print(f"TTS streaming error: {e}")
        
        # Return streaming response
        streaming_response = StreamingHttpResponse(
            generate_audio_stream(),
            content_type='audio/mpeg',
            headers={
                'Cache-Control': 'no-cache',
                'Content-Disposition': 'inline; filename="speech.mp3"',
                'Content-Length': str(len(audio_data)),
                'Accept-Ranges': 'bytes',
            }
        )
        
        return streaming_response
        
    except Exception as e:
        return JsonResponse(
            {'error': f'gTTS error: {str(e)}'},
            status=500
        )


@extend_schema(
    tags=['TTS'],
    summary='Test TTS functionality',
    description='Simple test endpoint to verify gTTS is working',
)
@api_view(['GET'])
def test_tts(request):
    """
    Test endpoint to verify gTTS functionality
    """
    try:
        from gtts import gTTS
        import io
        
        # Test with simple text
        test_text = "Hello, this is a test of the text to speech system."
        
        tts = gTTS(text=test_text, lang='en', tld='com', slow=False)
        
        # Use BytesIO to generate audio
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        audio_data = audio_buffer.getvalue()
        audio_buffer.close()
        
        return Response({
            'status': 'success',
            'message': 'gTTS is working correctly',
            'audio_size': len(audio_data),
            'test_text': test_text
        })
        
    except ImportError:
        return Response(
            {'error': 'gTTS library not installed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'gTTS test failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )