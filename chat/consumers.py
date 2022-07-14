import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Message
from django.utils import timezone

class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        messages = Message.objects.all()
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)
    
    def new_message(self, data):
        user_id = data['user']
        message_creat = Message.objects.create(
            user=user_id,
            text=data['message'],
            )
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message_creat)
        }
        return self.send_chat_message(content)
        
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
                'author': message.user,
                'content': message.text,
                'timestamp': str(message.time)
                }
        
    def send_message(self, message):
        self.send(text_data=json.dumps(message))
        
    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name,
        {
            "type": "chat_message",
            "message": message
        }
    )
    
    commands = {
    'fetch_messages': fetch_messages,
    'new_message': new_message
    }
    
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.commands[text_data_json['command']](self, text_data_json)
        # message = text_data_json['message']

        # # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))