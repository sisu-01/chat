from django import forms
from .models import ChatRoom

class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['room_name', 'max_count']
        labels = {
            'room_name' : '방 이름',
            'max_count' : '최대인원',
        }
