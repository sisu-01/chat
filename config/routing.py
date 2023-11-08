from django.urls import re_path

from chat.consumers import ChatConsumer
from rps.consumers import RpsConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/rps/(?P<room_id>\w+)/$", RpsConsumer.as_asgi()),
]
