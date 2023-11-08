from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from utils import get_client_ip, show_ip
from .models import RpsRoom, RpsRooms_Users
from .forms import RpsRoomForm
import datetime
import uuid
import json

"""
    rps 로비
"""
def index(request):
    room_id = request.GET.get('c', None)
    if room_id:
        context = {'room_id':room_id}
        response = render(request, 'rps/invite.html', context)
        tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
        expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
        response.set_cookie('CID',0,expires=expires)
        return response
    else:
        response = render(request, 'rps/loby.html')
        tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
        expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
        response.set_cookie('CID',0,expires=expires)
        return response

"""
    rps 로비 방 목록
"""
@require_http_methods("POST")
def room_list(request):
    try:
        res = list(RpsRoom.objects.all().values())
        result = True
        mess = '성공'
    except Exception as e:
        res = None
        result = False
        mess = str(e)+'\n관리자에게 문의하세요.'

    response = {'result':result,'mess':mess,'res':res}
    return JsonResponse(response, safe=False)

"""
    rps 방 입장 검사
"""
@require_http_methods("POST")
def room_knock(request):
    param = json.loads(request.body)
    room_id = param['room_id']
    user_uuid = param['user_uuid']
    try:
        if not user_uuid:
            user_uuid = uuid.uuid4()
        result = True
        try:
            temp = RpsRoom.objects.get(id=room_id)
            if(temp.current_user >= temp.maximum_user):
                mess = '이 방은 용량에 도달했습니다.'
                enter = False
            elif(temp.room_state==1):
                mess = '이미 게임이 시작됐습니다.'
                enter = False
            else:
                try:
                    test = RpsRooms_Users.objects.get(room=room_id,user_uuid=user_uuid)
                    mess = '이미 이 방에 접속하고 있습니다.'
                    enter = False
                except RpsRooms_Users.DoesNotExist:
                    mess = '성공'
                    enter = True
        except RpsRoom.DoesNotExist:
            mess = '방이 존재하지 않습니다.'
            enter  = False
    except Exception as e:
        result = False
        mess = str(e)+'\n관리자에게 문의하세요.'
        enter = False
    response = {
        'result'    : result,
        'mess'      : mess,
        'room_id'   : room_id,
        'user_uuid' : user_uuid,
        'enter'     : enter
    }
    return JsonResponse(response, safe=False)

"""
    chat 방 상세
"""
def room(request):
    if request.method == 'POST':
        #if int(request.COOKIES.get('CID')) == 0:
        user_uuid = request.POST.get('user_uuid')
        if not user_uuid:
            user_uuid = uuid.uuid4()
        #참가
        if request.POST.get('room_id'):
            user_list = RpsRoom.objects.get(id=request.POST.get('room_id')).rpsrooms_users_set.all()
            room_name = RpsRoom.objects.get(id=request.POST.get('room_id')).room_name
            user_ip = get_client_ip(request)
            context = {
                'room_id'   : request.POST.get('room_id'),
                'room_name' : room_name,
                'user_list' : user_list,
                'user_uuid' : user_uuid,
                'user_ip'   : show_ip(user_ip),
            }
            response = render(request, "rps/room.html", context)
            tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
            expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
            response.set_cookie('CID',1,expires=expires)
            return response
        #신규생성
        else:
            form = RpsRoomForm(request.POST)
            if form.is_valid():
                rpsRoom = form.save(commit=False)
                rpsRoom.current_user = 0;
                rpsRoom.room_state = 0;
                rpsRoom.host_uuid = 0;
                rpsRoom.save()
                user_ip = get_client_ip(request)
                context = {
                    'room_id'   : rpsRoom.id,
                    'room_name' : rpsRoom.room_name,
                    'user_uuid' : user_uuid,
                    'user_ip'   : show_ip(user_ip),
                }
                response = render(request, "rps/room.html", context)
                tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=14, minute=59, second=59)
                expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S UTC")
                response.set_cookie('CID',1,expires=expires)
                return response
    return redirect('/rps/')
