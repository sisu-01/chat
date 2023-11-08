"""
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatRoom

channel_layer = get_channel_layer()

@receiver(post_save, sender=ChatRoom)
def create_room_signal(sender, instance, created, *args, **kwargs):
    ins_id = instance.id
    ins_room_name = instance.room_name
    ins_user_count = instance.user_count

    if created:
        async_to_sync(channel_layer.group_send)(
            f'online_chat_room',
            {
                "type" : "websocket_room_added",
                "command" : "room_added",
                "room_id" : ins_id,
                "room_name" : ins_room_name,
                "user_count" : ins_user_count,
            }
        )

@receiver(post_save, sender=ChatRoom)
def create_room_signal(sender, instance, created, *args, **kwargs):
    ins_id = instance.id
    ins_room_name = instance.room_name
    ins_user_count = instance.user_count

    if created:
        async_to_sync(channel_layer.group_send)(
            f'online_chat_room',
            {
                "type" : "websocket_room_added",
                "command" : "room_added",
                "room_id" : ins_id,
                "room_name" : ins_room_name,
                "user_count" : ins_user_count,
            }
        )

@receiver(post_delete, sender=ChatRoom)
def create_room_signal(sender, instance, *args, **kwargs):
    ins_room_name = instance.room_name
    ins_id = instance.id
    async_to_sync(channel_layer.group_send)(
        f'online_chat_room',
        {
            "type" : "websocket_room_deleted",
            "command" : "room_deleted",
            "room_name" : ins_room_name,
            "room_id" : ins_id,
        }
    )
"""
