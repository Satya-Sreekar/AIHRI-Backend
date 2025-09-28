from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiExample


class BedrockRequestSerializer(serializers.Serializer):
    """
    Serializer for AWS Bedrock API requests
    """
    model = serializers.CharField(
        max_length=100,
        default="meta.llama3-8b-instruct-v1:0",
        help_text="The name of the AWS Bedrock model to use (e.g., 'meta.llama3-8b-instruct-v1:0', 'amazon.titan-text-express-v1', 'anthropic.claude-3-5-sonnet-20240620-v1:0')"
    )
    prompt = serializers.CharField(
        help_text="The prompt to send to the model"
    )
    stream = serializers.BooleanField(
        default=True,
        help_text="Whether to stream the response (default: True)"
    )
    options = serializers.DictField(
        required=False,
        help_text="Additional options for the model (temperature, top_p, max_tokens, etc.)"
    )

# Legacy serializer for backward compatibility
class OllamaRequestSerializer(BedrockRequestSerializer):
    """
    Legacy serializer for Ollama API requests (now redirects to Bedrock)
    """
    pass


class BedrockResponseSerializer(serializers.Serializer):
    """
    Serializer for AWS Bedrock API responses
    """
    model = serializers.CharField(
        help_text="The name of the model used"
    )
    created_at = serializers.CharField(
        help_text="Timestamp when the response was created"
    )
    response = serializers.CharField(
        help_text="The generated response from the model"
    )
    done = serializers.BooleanField(
        help_text="Whether the response is complete"
    )
    usage = serializers.DictField(
        required=False,
        help_text="Token usage information"
    )
    stop_reason = serializers.CharField(
        required=False,
        help_text="Reason why the generation stopped"
    )

# Legacy serializer for backward compatibility
class OllamaResponseSerializer(BedrockResponseSerializer):
    """
    Legacy serializer for Ollama API responses (now redirects to Bedrock)
    """
    context = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Context tokens for the response (legacy)"
    )
    total_duration = serializers.IntegerField(
        required=False,
        help_text="Total duration of the generation in nanoseconds (legacy)"
    )
    load_duration = serializers.IntegerField(
        required=False,
        help_text="Time taken to load the model in nanoseconds (legacy)"
    )
    prompt_eval_duration = serializers.IntegerField(
        required=False,
        help_text="Time taken to evaluate the prompt in nanoseconds (legacy)"
    )
    eval_duration = serializers.IntegerField(
        required=False,
        help_text="Time taken to generate the response in nanoseconds (legacy)"
    )


class TTSRequestSerializer(serializers.Serializer):
    """
    Serializer for gTTS Text-to-Speech API requests
    """
    text = serializers.CharField(
        help_text="The text to convert to speech"
    )
    lang = serializers.CharField(
        max_length=10,
        default="en",
        help_text="Language code (en, es, fr, de, it, etc.)"
    )
    tld = serializers.CharField(
        max_length=10,
        default="com",
        help_text="Top level domain for localized voices (com, co.uk, ca, etc.)"
    )
    slow = serializers.BooleanField(
        default=False,
        help_text="Speak slowly"
    ) 