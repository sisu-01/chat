from django.db import models

#this table will only exists when there are people in room
#once all the users are gone this will be deleted
class ChatRoom(models.Model):
    room_name = models.CharField(max_length=50)
    user_count = models.IntegerField(null=True)
    max_count = models.IntegerField(null=True)

    def __str__(self) -> str:
        return self.room_name

class TrackPlayers(models.Model):
    username =  models.CharField(max_length=50)
    uuid =  models.CharField(max_length=36)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.username
