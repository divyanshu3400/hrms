from django.urls import path
from .consumers import UserConsumer, TestConsumer

websocket_urlpatterns = [
    path("ws/users/", UserConsumer.as_asgi()),
    path("ws/tests/", TestConsumer.as_asgi()),
]
