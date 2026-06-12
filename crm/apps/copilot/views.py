from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from .agent import CopilotAgent


class _ChatMessage(serializers.Serializer):
    role = serializers.ChoiceField(choices=['system', 'user', 'assistant', 'tool'])
    content = serializers.CharField(allow_blank=True)


class CopilotChatRequest(serializers.Serializer):
    messages = _ChatMessage(many=True)
    context = serializers.DictField(required=False)


class CopilotAgentRequest(serializers.Serializer):
    goal = serializers.CharField(help_text='High-level marketing goal in plain English.')
    context = serializers.DictField(required=False)


_CopilotResponse = inline_serializer(
    name='CopilotResponse',
    fields={
        'response_text': serializers.CharField(),
        'tool_calls_made': serializers.ListField(child=serializers.CharField()),
        'created_objects': serializers.DictField(),
    },
)


@extend_schema(tags=['copilot'])
class CopilotChatView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Chat with the AI Copilot',
        description='Multi-turn chat. The Copilot can call tools (live DB queries) before replying.',
        request=CopilotChatRequest,
        responses={200: _CopilotResponse},
        examples=[
            OpenApiExample(
                'Ask about top campaigns',
                value={'messages': [{'role': 'user', 'content': 'What are my top 3 campaigns by click rate?'}]},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        messages = request.data.get('messages', [])
        context = request.data.get('context', {})
        if not messages:
            return Response({'error': 'messages required'}, status=400)
        result = CopilotAgent().run(messages, context, mode='chat')
        return Response(result)


@extend_schema(tags=['copilot'])
class CopilotAgentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Run the Copilot in agent mode',
        description=(
            'Give the agent a goal; it autonomously counts the audience, drafts a segment, '
            'writes message variants, and creates a draft campaign — never launching it.'
        ),
        request=CopilotAgentRequest,
        responses={200: _CopilotResponse},
        examples=[
            OpenApiExample(
                'Re-engage at-risk customers',
                value={'goal': 'Re-engage Mumbai high-spenders who haven\'t bought in 60 days with a 15% offer.'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        goal = request.data.get('goal') or ''
        context = request.data.get('context', {})
        if not goal:
            return Response({'error': 'goal required'}, status=400)
        messages = [{'role': 'user', 'content': goal}]
        result = CopilotAgent().run(messages, context, mode='agent')
        return Response(result)
