import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer

class GameComsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"game_{self.game_id}"

        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.user = query_params.get('user', [None])[0] 
        print('usersname',self.user)

        if not self.user:
            print('Closing the connection no username is provided')
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Broadcast the user's online status to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'user_status',
                'user': self.user,
                'status' : 'online'
            }
        )


    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'user'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.user,
                    'status': 'offline'
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        if action == 'online-status':
            # Broadcast online status to the group
            online = text_data_json.get('online', 'offline')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.user,
                    'status': online
                }
            )

    async def user_status(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'online-status',
            'user': event['user'],
            'status': event['status']
        }))
    
