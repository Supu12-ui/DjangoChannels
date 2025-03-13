from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    rooms = set()  # Keep track of all active rooms

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Store room in set of active rooms
        ChatConsumer.rooms.add(self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove room when disconnecting
        ChatConsumer.rooms.discard(self.room_group_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data.get("username", "Anonymous")

        # Send message to ALL rooms
        for room in ChatConsumer.rooms:
            await self.channel_layer.group_send(
                room,  # Broadcast to all rooms
                {
                    "type": "chat_message",
                    "message": message,
                    "username": username
                }
            )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(text_data=json.dumps({
            "message": message,
            "username": username
        }))
