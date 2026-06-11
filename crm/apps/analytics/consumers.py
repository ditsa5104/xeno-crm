import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EventsConsumer(AsyncJsonWebsocketConsumer):
    GROUP = 'events'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'hello', 'message': 'connected'})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def channel_event(self, event):
        await self.send_json(event['data'])
