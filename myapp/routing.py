from django.urls import re_path
from . import consumers,views

websocket_urlpatterns = [
    re_path(r'ws/group_chat/(?P<group_id>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r'ws/private_chat/(?P<receiver_id>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    re_path('ws/group_chat/<int:group_id>/', views.GroupChatConsumer.as_asgi()),
]