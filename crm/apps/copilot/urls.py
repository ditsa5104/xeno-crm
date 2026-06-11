from django.urls import path
from .views import CopilotChatView, CopilotAgentView

urlpatterns = [
    path('chat/', CopilotChatView.as_view()),
    path('agent/', CopilotAgentView.as_view()),
]
