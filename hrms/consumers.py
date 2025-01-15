from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import logging

logger = logging.getLogger(__name__)

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connected.")
        await self.accept()
        await self.send_initial_data()

    @database_sync_to_async
    def fetch_users(self):
        from hrms_app.models import CustomUser 
        users = CustomUser.objects.all().values('id', 'username','first_name','last_name', 'email')
        return list(users)

    async def send_initial_data(self):
        users = await self.fetch_users()
        await self.send(text_data=json.dumps({'users': users}))

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected.")

    async def receive(self, text_data):
        logger.info("Received data from client: %s", text_data)

    async def user_change_event(self, event):
        logger.info("Received user change event.")
        users = await self.fetch_users()
        await self.send(text_data=json.dumps({'users': users}))

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data="WebSocket connection established.")

    async def disconnect(self, close_code):
        # Clean up when the WebSocket connection is closed.
        pass

    async def receive(self, text_data):
        # Receive a message from the WebSocket.
        pass
