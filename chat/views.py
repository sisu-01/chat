from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from utils import get_client_ip
from .models import ChatRoom, TrackPlayers
from .forms import ChatRoomForm
import datetime
import uuid
import json

#from channels.layers import get_channel_layer
#groups = get_channel_layer().groups

"""
    chat 로비
"""
def index(request):
    room_id = request.GET.get('c', None)
    if room_id:
        context = {'room_id':room_id}
        response = render(request, 'chat/invite.html', context)
        tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
        expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
        response.set_cookie('CID',0,expires=expires)
        return response
    else:
        response = render(request, 'chat/loby.html')
        tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
        expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
        response.set_cookie('CID',0,expires=expires)
        return response

"""
    chat 로비 방 목록
"""
@require_http_methods("POST")
def room_list(request):
    #res = [{"room_name":x.room_name,"room_id":x.id,"user_count":x.user_count}for x in ChatRoom.objects.all()]
    try:
        res = list(ChatRoom.objects.all().values())
        result = True
        mess = '성공'
    except Exception as e:
        res = None
        result = False
        mess = str(e)+'\n관리자에게 문의하세요.'

    response = {'result':result,'mess':mess,'res':res}
    return JsonResponse(response, safe=False)

"""
    chat 방 입장 검사
"""
@require_http_methods("POST")
def room_knock(request):
    param = json.loads(request.body)
    room_id = param['room_id']
    user_uuid = param['uuid']
    try:
        if not user_uuid:
            user_uuid = uuid.uuid4()
        result = True
        try:
            temp = ChatRoom.objects.get(id=room_id)
            if(temp.user_count >= temp.max_count):
                mess = '이 방은 용량에 도달했습니다.'
                enter = False
            else:
                try:
                    test = TrackPlayers.objects.get(room=room_id,uuid=user_uuid)
                    mess = '이미 이 방에 접속하고 있습니다.'
                    enter = False
                except TrackPlayers.DoesNotExist:
                    mess = '성공'
                    enter = True
        except ChatRoom.DoesNotExist:
            mess = '방이 존재하지 않습니다.'
            enter  = False
    except Exception as e:
        result = False
        mess = str(e)+'\n관리자에게 문의하세요.'
        enter = False
    response = {
        'result':result,
        'mess':mess,
        'room_id':room_id,
        'uuid':user_uuid,
        'enter':enter
    }
    return JsonResponse(response, safe=False)

"""
    chat 방 상세
"""
def room(request):
    if request.method == 'POST':
        if int(request.COOKIES.get('CID')) == 0:
            user_uuid = request.POST.get('uuid')
            if not user_uuid:
                user_uuid = uuid.uuid4()
            #참가
            if request.POST.get('room_id'):
                room_name = ChatRoom.objects.get(id=request.POST.get('room_id')).room_name
                ip = get_client_ip(request)
                context = {
                    'room_id':request.POST.get('room_id'),
                    'room_name':room_name,
                    'uuid':user_uuid,
                    'ip':ip
                }
                response = render(request, "chat/room.html", context)
                tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
                expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
                response.set_cookie('CID',1,expires=expires)
                return response
            #신규생성
            else:
                form = ChatRoomForm(request.POST)
                if form.is_valid():
                    chatRoom = form.save(commit=False)
                    chatRoom.user_count = 0;
                    chatRoom.save()
                    ip = get_client_ip(request)
                    context = {
                        'room_id':chatRoom.id,
                        'room_name':chatRoom.room_name,
                        'uuid': user_uuid,
                        'ip':ip
                    }
                    response = render(request, "chat/room.html", context)
                    tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
                    expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
                    response.set_cookie('CID',1,expires=expires)
                    return response
    return redirect('/chat/')
