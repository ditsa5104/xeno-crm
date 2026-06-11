from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .agent import CopilotAgent


class CopilotChatView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        messages = request.data.get('messages', [])
        context = request.data.get('context', {})
        if not messages:
            return Response({'error': 'messages required'}, status=400)
        result = CopilotAgent().run(messages, context, mode='chat')
        return Response(result)


class CopilotAgentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        goal = request.data.get('goal') or ''
        context = request.data.get('context', {})
        if not goal:
            return Response({'error': 'goal required'}, status=400)
        messages = [{'role': 'user', 'content': goal}]
        result = CopilotAgent().run(messages, context, mode='agent')
        return Response(result)
