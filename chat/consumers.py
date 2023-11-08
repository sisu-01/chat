from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
from .models import ChatRoom,TrackPlayers
import json

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id = "chat_%s" % self.room_id
        await self.get_room()
        self.user_uuid=''
        await self.channel_layer.group_add(
            self.room_group_id,
            self.channel_name
        )
        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        username = content.get("username", None)
        uuid = content.get("uuid", None)
        clientIp = content.get("clientIp", None)

        if command == "joined":
            info = content.get("info", None)

            await self.create_players(username, uuid)
            self.user_name = username
            self.user_uuid = uuid

            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type": "websocket_joined",
                    "command": command,
                    "info" : info,
                    "username" : username,
                    "uuid" : uuid,
                    "clientIp": clientIp,
                }
            )
        if command == "chat":
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type": "websocket_chat",
                    "command":command,
                    "chat": content.get("chat", None),
                    "username":username,
                    "uuid": uuid,
                    "clientIp": clientIp,

                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_id,
            {
                "type": "websocket_leave",
                "info":f"{self.user_name} left room",

            }
        )
        await self.delete_player()
        await self.channel_layer.group_discard(
            self.room_group_id,
            self.channel_name
        )

    async def websocket_joined(self, event):
        await self.players_count()
        await self.send_json(({
             'command':event["command"],
             'info':event["info"],
             'username':event["username"],
             'uuid':event["uuid"],
             'clientIp':event["clientIp"],
             'all_players':self.all_players_for_room,
             'users_count':self.players_count_all,
        }))

    async def websocket_chat(self, event):
        await self.send_json(({
            "command" : event["command"],
            "chat" : event["chat"],
            "username" : event["username"],
            "uuid" : event["uuid"],
            "clientIp": event["clientIp"],
        }))

    async def websocket_leave(self, event):
        await self.players_count()
        await self.send_json(({
            'command':'joined',
            'info':event["info"],
            "users_count":self.players_count_all,
            "all_players":self.all_players_for_room,
        }))

    @database_sync_to_async
    def get_room(self):
        self.chat_room = ChatRoom.objects.get(id=self.room_id)

    @database_sync_to_async
    def create_players(self, username, uuid):
        TrackPlayers.objects.get_or_create(room=self.chat_room,username=username,uuid=uuid)

    @database_sync_to_async
    def players_count(self):
        self.all_players_for_room = [x.username for x in self.chat_room.trackplayers_set.all()]
        self.players_count_all = self.chat_room.trackplayers_set.all().count()
        self.chat_room.user_count = self.players_count_all
        self.chat_room.save()

    @database_sync_to_async
    def delete_player(self):
        TrackPlayers.objects.get(room=self.chat_room,uuid=self.user_uuid).delete()
        self.players_count_all = self.chat_room.trackplayers_set.all().count()
        self.chat_room.user_count = self.players_count_all
        self.chat_room.save()
        if self.chat_room.user_count == 0:
            self.chat_room.delete()
