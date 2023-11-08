from django.db import models

class RpsRoom(models.Model):
    #방 이름
    room_name = models.CharField(max_length=50)
    #현재 인원
    current_user = models.IntegerField()
    #최대 인원
    maximum_user = models.IntegerField()
    #방 상태
    #0 : 대기중 / 1 : 게임 진행중
    room_state = models.IntegerField()
    #방장
    host_uuid =  models.CharField(max_length=36)

    def __str__(self) -> str:
        return self.room_name

class RpsRooms_Users(models.Model):
    #유저 이름
    user_name =  models.CharField(max_length=50)
    #유저 아이디
    user_uuid =  models.CharField(max_length=36)
    #유저 ip
    user_ip = models.CharField(max_length=40)
    #방장
    #0 : 일반 / 1 : 방장
    user_host =  models.IntegerField()
    #준비 상태
    #0 : 대기중 / 1 : 준비
    user_state = models.IntegerField()
    #접속 방
    room = models.ForeignKey(RpsRoom, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user_name
