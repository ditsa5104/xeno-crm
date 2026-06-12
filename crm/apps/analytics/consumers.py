import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EventsConsumer(AsyncJsonWebsocketConsumer):
    GROUP = 'events'

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'hello', 'message': 'connected'})

    async def disconnect(self, code):
        if self.scope.get('user') and self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def channel_event(self, event):
        await self.send_json(event['data'])
