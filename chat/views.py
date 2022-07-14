from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.http import HttpResponse
# Create your views here.

@login_required
def index(request):
    return render(request, 'chat/index.html')

@login_required
def room(request, room_name):
    user = request.user.username
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'user': user,
    })