from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Profile
from .models import Connectionrequests

from .forms import RoomForm
from .models import Message, Room
from users import models


@login_required()
def chat_home(request):

    form = RoomForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        room_name = form.cleaned_data['room_name']
        db_messages = Message.objects.filter(room=room_name)[:]
        messages.success(request, f"Joined: {room_name}")
        return render(request, 'chat/chatroom.html', {'room_name': room_name, 'title': room_name, 'db_messages': db_messages})

    return render(request, 'chat/index.html', {'form': form})


@login_required
def chat_room(request, room_name):
    db_messages = Message.objects.filter(room=room_name)[:]

    messages.success(request, f"Joined: {room_name}")
    return render(request, 'chat/chatroom.html', {
        'room_name': room_name,
        'title': room_name,
        'db_messages': db_messages,
    })

@login_required
def viewallpeers(request):
    #profiles = models.Profile.objects.all()  # Fetch all profiles from the database
    if request.method == 'POST':
        #create request
        print()
    else:
        profiles = models.Profile.objects.exclude(user=request.user).exclude(user__is_staff=True)
        return render(request, 'chat/viewall.html', {'profiles': profiles})


@login_required
def send_connection_request(request, profile_id):
    sender = request.user.profile
    receiver = get_object_or_404(Profile, id=profile_id)
    
    # Check if a request already exists to avoid duplicates
    if not Connectionrequests.objects.filter(sender=sender, receiver=receiver).exists():
        Connectionrequests.objects.create(sender=sender, receiver=receiver)
    
    return redirect('viewall')  # Redirect back to the list of profiles


@login_required
def view_my_requests(request):
    # Get all pending connection requests received by the logged-in user
    if request.method == 'POST':
        #create request
        print()
    else:
        print("On to view connection request page")
        profile = request.user.profile
        received_requests = Connectionrequests.objects.filter(receiver=profile, is_approved=False)
        print("Recieved requests", received_requests)
        return render(request, 'chat/ViewConnectionRequests.html', {'received_requests': received_requests})


@login_required
def approve_connection_request(request, request_id):
    connection_request = get_object_or_404(Connectionrequests, id=request_id, receiver=request.user.profile)
    connection_request.is_approved = True
    print("Sender name = ", connection_request.sender.user.username)
    connection_request.chatroomname = "Chat with "+ connection_request.sender.user.username
    connection_request.save()
    
    return redirect('viewmyconnectionrequests')  # Redirect back to the list of requests

@login_required
def reject_connection_request(request, request_id):
    connection_request = get_object_or_404(Connectionrequests, id=request_id, receiver=request.user.profile)
    connection_request.delete()
    
    return redirect('viewmyconnectionrequests')  # Redirect back to the list of requests
