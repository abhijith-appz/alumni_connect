# ai_assistant/api_urls.py
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AIConversation, AIMessage


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_api(request):
    """
    Stateless API endpoint for AI chat.
    POST { "message": "...", "conversation_id": optional }
    Returns { "reply": "...", "conversation_id": int }
    """
    from .views import _call_ai
    message  = request.data.get('message', '').strip()
    conv_id  = request.data.get('conversation_id')

    if not message:
        return Response({'error': 'message is required'}, status=400)

    if conv_id:
        conv = AIConversation.objects.filter(pk=conv_id, user=request.user).first()
        if not conv:
            return Response({'error': 'conversation not found'}, status=404)
    else:
        title = message[:60] + ('…' if len(message) > 60 else '')
        conv  = AIConversation.objects.create(user=request.user, title=title)

    AIMessage.objects.create(conversation=conv, role=AIMessage.Role.USER, content=message)
    reply = _call_ai(conv, request.user)
    AIMessage.objects.create(conversation=conv, role=AIMessage.Role.ASSISTANT, content=reply)
    conv.save()

    return Response({'reply': reply, 'conversation_id': conv.pk})


urlpatterns = [
    path('chat/', chat_api, name='api_ai_chat'),
]
