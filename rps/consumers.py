from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
from .models import RpsRoom, RpsRooms_Users
import json

async def search_gamedata_index(data, id):
    try:
        if data[id]:
            return True
    except KeyError:
        return False

def getResult(gameInfo):
    command = ''
    count = 0
    rps = ''

    if len(gameInfo['r']): rps += 'r'
    if len(gameInfo['p']): rps += 'p'
    if len(gameInfo['s']): rps += 's'

    winRps = {
        'r'  : 'd',
        'p'  : 'd',
        's'  : 'd',
        'rps': 'd',
        'rp' : 'p',
        'ps' : 's',
        'rs' : 'r',
    }.get(rps, 'error')

    if winRps == 'd':
        command = 'draw'
        count = len(gameInfo['r'])+len(gameInfo['p'])+len(gameInfo['s'])
        winner  = None
    elif len(gameInfo[winRps]) == 1:
        command = 'end'
        count = None
        winner  = gameInfo[winRps]
    else:
        command = 'go'
        count = len(gameInfo[winRps])
        winner  = gameInfo[winRps]
    res = {
        'command' : command,
        'count'   : count,
        'winner'  : winner,
        'winRps'  : winRps,
        'gameInfo': gameInfo,
        }
    return res

def addRps(param):
    return len(param['r'])+len(param['p'])+len(param['s'])

game_data = {}

class RpsConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_id        = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id  = "rps_%s" % self.room_id
        self.user_uuid      = ""

        if not await search_gamedata_index(game_data, self.room_id):
            game_data[self.room_id] = {
                'round' : 1,
                'count' : 0,
                'users' : {
                    'r' : [],
                    'p' : [],
                    's' : [],
                },
            }

        await self.get_room()
        await self.channel_layer.group_add(
            self.room_group_id,
            self.channel_name
        )
        await self.accept()

    async def receive_json(self, content):
        command     = content.get("command", None)
        user_uuid   = content.get("user_uuid", None)
        user_name   = content.get("user_name", None)
        user_ip     = content.get("user_ip", None)

        if command == "joined":
            self.user_uuid = user_uuid
            self.user_name = user_name
            await self.create_user(user_uuid,user_name,user_ip)
            await self.count_current_user()
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type"      : "websocket_joined",
                    "command"   : command,
                    "user_uuid" : user_uuid,
                    "user_name" : user_name,
                    "user_ip"   : user_ip,
                    "current_user" : self.current_user,
                    "all_users" : self.all_users_for_room,
                }
            )
            if self.rps_room.host_uuid == "0":
                await self.set_host(user_uuid, user_name)
        if command == "chat":
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type"      : "websocket_chat",
                    "command"   : command,
                    "user_name" : user_name,
                    "user_ip"   : user_ip,
                    "chat"      : content.get("chat", None),
                }
            )
        if command == "host":
            print("host")

        if command == "state":
            user_state = content.get("user_state", None)
            await self.set_user_state(user_uuid, user_state)
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type"      : "websocket_state",
                    "command"   : command,
                    "user_uuid" : user_uuid,
                    "user_state": user_state,
                }
            )
        if command == "start":
            if await search_gamedata_index(game_data, self.room_id):
                game_data[self.room_id] = {
                    'round' : 1,
                    'count' : 0,
                    'users' : {
                        'r' : [],
                        'p' : [],
                        's' : [],
                    },
                }
                await self.set_room_state(1)
                await self.count_current_user()
                game_data[self.room_id]['count'] = self.current_user
                user_list = await self.select_game_user_list()

                await self.channel_layer.group_send(
                    self.room_group_id,
                    {
                        "type"      : "websocket_start",
                        "command"   : command,
                        "user_list" : user_list,
                    }
                )
            else:
                print('error gamedata is missing')
        if command == "rps":
            rps = content.get("rps", None)
            game_data[self.room_id]['users'][rps].append(user_uuid)
            if addRps(game_data[self.room_id]['users']) == game_data[self.room_id]['count']:
                temp = getResult(game_data[self.room_id]['users'])
                if temp['command'] == 'end':
                    await self.set_room_state(0)
                else:
                    game_data[self.room_id]['count'] = temp['count']
                    game_data[self.room_id]['round'] = game_data[self.room_id]['round']+1
                    game_data[self.room_id]['users'] = {
                        'r' : [],
                        'p' : [],
                        's' : [],
                    }
                await self.channel_layer.group_send(
                    self.room_group_id,
                    {
                        "type"      : "websocket_result",
                        "command"   : command,
                        "command2"  : temp['command'],
                        "round"     : game_data[self.room_id]['round'],
                        "winRps"    : temp['winRps'],
                        "gameInfo"  : temp['gameInfo'],
                    }
                )

    async def disconnect(self, close_code):
        print(await self.get_room_state())
        await self.channel_layer.group_discard(
            self.room_group_id,
            self.channel_name
        )
        print(await self.get_room_state())
        left = await self.get_user()
        print(await self.get_room_state())
        await self.delete_user()
        print(await self.get_room_state())
        await self.count_current_user()
        print(await self.get_room_state())
        if self.rps_room.current_user == 0:
            print(await self.get_room_state())
            await self.delete_room()
            print(await self.get_room_state())
        else:
            print(await self.get_room_state())
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type"      : "websocket_leave",
                    "command"   : "lefted",
                    "user_uuid" : self.user_uuid,
                    "user_name" : self.user_name,
                    "current_user" : self.current_user,
                    "all_users" : self.all_users_for_room,
                }
            )
            print(await self.get_room_state())
            if left.user_host == 1:
                print(await self.get_room_state())
                next_host = await self.get_next_host()
                print(await self.get_room_state())
                await self.set_host(next_host.user_uuid, next_host.user_name)
                print(await self.get_room_state())

    async def set_host(self, user_uuid, user_name):
        await self.update_host(user_uuid)
        await self.channel_layer.group_send(
            self.room_group_id,
            {
                "type"      : "websocket_host",
                "command"   : "host",
                "user_uuid" : user_uuid,
                "user_name" : user_name,
            }
        )

    async def websocket_joined(self, event):
        await self.send_json(({
             "command"      : event["command"],
             "user_uuid"    : event["user_uuid"],
             "user_name"    : event["user_name"],
             "user_ip"      : event["user_ip"],
             "current_user" : event["current_user"],
             "all_users"    : event["all_users"],
        }))
    async def websocket_host(self, event):
        await self.send_json(({
             "command"  : event["command"],
             "user_uuid": event["user_uuid"],
             "user_name": event["user_name"],
        }))
    async def websocket_chat(self, event):
        await self.send_json(({
            "command"   : event["command"],
            "user_name" : event["user_name"],
            "user_ip"   : event["user_ip"],
            "chat"      : event["chat"],
        }))
    async def websocket_state(self, event):
        await self.send_json(({
            "command"   : event["command"],
            "user_uuid" : event["user_uuid"],
            "user_state": event["user_state"],
        }))
    async def websocket_start(self, event):
        await self.send_json(({
            "command"   : event["command"],
            "user_list" : event["user_list"],
        }))
    async def websocket_result(self, event):
        await self.send_json(({
            "command"   : event["command"],
            "command2"  : event["command2"],
            "round"     : event["round"],
            "winRps"    : event["winRps"],
            "gameInfo"  : event["gameInfo"],
        }))

    async def websocket_leave(self, event):
        await self.send_json(({
            "command"   : event["command"],
            "user_uuid" : event["user_uuid"],
            "user_name" : event["user_name"],
            "current_user": event["current_user"],
            "all_users" : event["all_users"],
        }))

    @database_sync_to_async
    def get_room(self):
        self.rps_room = RpsRoom.objects.get(id=self.room_id)

    @database_sync_to_async
    def get_user(self):
        return RpsRooms_Users.objects.get(user_uuid=self.user_uuid)

    @database_sync_to_async
    def get_next_host(self):
        return RpsRooms_Users.objects.filter(room=self.rps_room).order_by("id")[0]

    @database_sync_to_async
    def update_host(self, user_uuid):
        self.rps_room.host_uuid = user_uuid
        self.rps_room.save()
        temp = RpsRooms_Users.objects.filter(user_uuid=user_uuid).update(user_host=1,user_state=1)

    @database_sync_to_async
    def set_room_state(self, state):
        self.rps_room.room_state = state
        self.rps_room.save()

    @database_sync_to_async
    def set_user_state(self, user_uuid, user_state):
        RpsRooms_Users.objects.filter(user_uuid=user_uuid).update(user_state=user_state)

    @database_sync_to_async
    def create_user(self,user_uuid,user_name,user_ip):
        RpsRooms_Users.objects.get_or_create(room=self.rps_room,user_uuid=user_uuid,user_name=user_name,user_ip=user_ip,user_host=0,user_state=0)

    @database_sync_to_async
    def count_current_user(self):
        self.current_user = self.rps_room.rpsrooms_users_set.all().count()
        self.rps_room.current_user = self.current_user
        self.rps_room.save()
        self.all_users_for_room = [x.user_name for x in self.rps_room.rpsrooms_users_set.all()]

    @database_sync_to_async
    def select_game_user_list(self):
        return [{'user_name':x.user_name,'user_uuid':x.user_uuid} for x in self.rps_room.rpsrooms_users_set.all()]

    @database_sync_to_async
    def delete_user(self):
        RpsRooms_Users.objects.get(room=self.rps_room,user_uuid=self.user_uuid).delete()

    @database_sync_to_async
    def delete_room(self):
        del(game_data[self.room_id])
        self.rps_room.delete()

    @database_sync_to_async
    def get_room_state(self):
        return RpsRoom.objects.get(id=self.room_id).room_state