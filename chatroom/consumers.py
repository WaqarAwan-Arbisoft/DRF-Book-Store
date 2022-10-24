"""
Consumer for sending and receiving messages through the socket
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bookshop_chat'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        name = text_data_json['sender']['name']
        id = text_data_json['sender']['id']
        email = text_data_json['sender']['email']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'sender': {
                    'name': name,
                    'id': id,
                    'email': email
                }
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        name = event['sender']['name']
        id = event['sender']['id']
        email = event['sender']['email']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': {
                'name': name,
                'id': id,
                'email': email
            }
        }))
