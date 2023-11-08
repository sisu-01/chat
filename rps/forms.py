from django import forms
from .models import RpsRoom

class RpsRoomForm(forms.ModelForm):
    class Meta:
        model = RpsRoom
        fields = ['room_name', 'maximum_user']
        labels = {
            'room_name' : '방 이름',
            'maximum_user' : '최대인원',
        }
