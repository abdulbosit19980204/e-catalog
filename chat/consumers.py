import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        # Verify conversation existence and user membership
        if not await self.is_member():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            body = data.get('body')
            if body:
                message = await self.save_message(body)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': message.id,
                            'body': message.body,
                            'sender_id': message.sender_id,
                            'sender_username': message.sender.username,
                            'created_at': str(message.created_at),
                        }
                    }
                )
        elif message_type == 'read_receipt':
            # Handle read status updates if needed
            pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def is_member(self):
        user = self.scope['user']
        if not user.is_authenticated:
            return False
            
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            # Allow the user who started the chat or any staff user (admin/supervisor)
            return conversation.user == user or user.is_staff
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, body):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=self.scope['user'],
            body=body
        )
        # Update conversation last message time
        conversation.save() # Auto-updates updated_at/last_message_at
        return message
