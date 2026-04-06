# """
# ASGI config for ride_booking project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.urls import path

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ride_booking.settings')

# # Simple WebSocket consumer for testing
# class TestConsumer:
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data="Connected to WebSocket")

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter([
#             path('ws/test/', TestConsumer.as_asgi()),
#         ])
#     ),
# })



# ride_booking/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from channels.generic.websocket import WebsocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ride_booking.settings')

# Define a simple test consumer
class TestConsumer(WebsocketConsumer):
    def connect(self):
        # Accept the WebSocket connection
        self.accept()
        # Send a welcome message
        self.send(text_data="Connected to WebSocket successfully!")
    
    def disconnect(self, close_code):
        # Handle disconnection
        pass
    
    def receive(self, text_data):
        # Handle incoming messages
        self.send(text_data=f"Echo: {text_data}")

# Define URL routing for WebSockets
websocket_urlpatterns = [
    path('ws/test/', TestConsumer.as_asgi()),
]

# Main ASGI application
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
