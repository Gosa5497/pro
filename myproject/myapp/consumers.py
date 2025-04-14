from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import PrivateMessage, User
from django.utils.timezone import now
from asgiref.sync import sync_to_async

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'private_chat_{self.receiver_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']
        file_url = data.get('file_url')

        # Save message to the database
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=self.receiver_id)

        await sync_to_async(PrivateMessage.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message,
            file=file_url,
            message_type='text' if not file_url else 'file'
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'file_url': file_url
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'file_url': event['file_url']
        }))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from .models import GroupMessage, ChatGroup

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_id = None
        self.user = None
        self.room_group_name = None

    async def connect(self):
        """Handles WebSocket connection with authentication and permission checks."""
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.user = self.scope["user"]
        self.room_group_name = f'group_chat_{self.group_id}'

        if not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return

        try:
            # Verify user has permission to access this group
            group = await self.get_group()
            if not await self.user_can_access_group(group):
                await self.close(code=4003)  # Forbidden
                return

            # Add to WebSocket group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

        except ObjectDoesNotExist:
            await self.close(code=4004)  # Group not found
        except Exception as e:
            print(f"Connection error: {e}")
            await self.close(code=4000)  # Generic error

    async def disconnect(self, close_code):
        """Cleanly disconnect from WebSocket group."""
        if hasattr(self, 'room_group_name') and self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages with different actions."""
        try:
            data = json.loads(text_data)
            action = data.get('action', 'new_message')  # Default action

            if action == 'new_message':
                await self.handle_new_message(data)
            elif action == 'edit_message':
                await self.handle_edit_message(data)
            elif action == 'delete_message':
                await self.handle_delete_message(data)
            elif action == 'typing':
                await self.handle_typing_indicator(data)
            else:
                raise ValueError("Invalid action type")

        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except PermissionDenied as e:
            await self.send_error(str(e))
        except Exception as e:
            print(f"Error processing message: {e}")
            await self.send_error("An error occurred")

    async def handle_new_message(self, data):
        """Process and broadcast a new message."""
        message_type = data.get('message_type', 'text')
        content = data.get('content', '')
        file_url = data.get('file_url')

        # Create and save the message
        message = await self.create_message(
            message_type=message_type,
            content=content,
            file_url=file_url
        )

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'new',
                'message_id': message.id,
                'sender': self.user.username,
                'content': content,
                'message_type': message_type,
                'file_url': file_url,
                'timestamp': message.timestamp.isoformat(),
            }
        )

    async def handle_edit_message(self, data):
        """Process message edits."""
        message_id = data['message_id']
        new_content = data.get('content')
        new_file_url = data.get('file_url')

        message = await self.update_message(
            message_id=message_id,
            new_content=new_content,
            new_file_url=new_file_url
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'edit',
                'message_id': message.id,
                'sender': message.sender.username,
                'content': new_content,
                'message_type': message.message_type,
                'file_url': message.file.url if message.file else None,
                'timestamp': message.edited.isoformat() if message.edited else message.timestamp.isoformat(),
            }
        )

    async def handle_delete_message(self, data):
        """Process message deletion."""
        message_id = data['message_id']
        await self.delete_message(message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'delete',
                'message_id': message_id,
            }
        )

    async def handle_typing_indicator(self, data):
        """Broadcast typing indicator to group."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'typing',
                'sender': self.user.username,
                'is_typing': data.get('is_typing', True),
            }
        )

    async def chat_message(self, event):
        """Send processed messages to WebSocket clients."""
        await self.send(text_data=json.dumps(event))

    async def send_error(self, error_message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'status': 'error',
            'message': error_message
        }))

    @database_sync_to_async
    def get_group(self):
        """Get group with permission check."""
        return ChatGroup.objects.get(id=self.group_id)

    @database_sync_to_async
    def user_can_access_group(self, group):
        """Verify user has permission to access this group."""
        return group.can_communicate(self.user)

    @database_sync_to_async
    def create_message(self, message_type, content, file_url=None):
        """Create and save a new group message."""
        group = ChatGroup.objects.get(id=self.group_id)
        return GroupMessage.objects.create(
            group=group,
            sender=self.user,
            content=content,
            message_type=message_type,
            file=file_url
        )

    @database_sync_to_async
    def update_message(self, message_id, new_content, new_file_url=None):
        """Update an existing message with permission check."""
        message = GroupMessage.objects.get(id=message_id)
        
        # Verify user can edit this message
        if message.sender != self.user and not self.user in message.group.admins.all():
            raise PermissionDenied("You don't have permission to edit this message")

        if new_content:
            message.content = new_content
        if new_file_url:
            message.file = new_file_url
            message.message_type = self.determine_message_type(new_file_url)
        
        message.edited = timezone.now()
        message.save()
        return message

    @database_sync_to_async
    def delete_message(self, message_id):
        """Soft delete a message with permission check."""
        message = GroupMessage.objects.get(id=message_id)
        
        # Verify user can delete this message
        if message.sender != self.user and not self.user in message.group.admins.all():
            raise PermissionDenied("You don't have permission to delete this message")

        message.soft_delete()

    def determine_message_type(self, file_url):
        """Determine message type based on file extension."""
        if not file_url:
            return 'text'
        
        file_name = file_url.lower()
        if any(ext in file_name for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return 'image'
        elif any(ext in file_name for ext in ['.mp4', '.mov', '.avi']):
            return 'video'
        else:
            return 'file'