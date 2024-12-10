from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Profile
from .models import Connectionrequests
from django.db.models import Q
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
    
    else:
        profile = request.user.profile
        approved_requests = Connectionrequests.objects.filter(
        is_approved=True
        ).filter(
        Q(sender=profile) | Q(receiver=profile)
        )
    
        return render(request, 'chat/index.html', {'form': form, 'approved_requests': approved_requests})
       # return render(request, 'chat/index.html', {'form': form})

@login_required
def chat_room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    db_messages = Message.objects.filter(room=room).order_by('timestamp')[:]
    
    return render(request, 'chat/chatroom.html', {
        'room_name': room.name,
        'title': room.name,
        'db_messages': db_messages,
    })

# File upload handler
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def upload_file(request, room_name):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        path = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))
        return JsonResponse({'file_url': default_storage.url(path)})
    return JsonResponse({'error': 'No file uploaded'}, status=400)

@login_required
def viewallpeers(request):
    if request.method == 'POST':
        # Handle POST logic for creating requests (not implemented in this example)
        print()
    else:
        # Fetch profiles excluding the logged-in user, staff users, and existing connections
        existing_connections = Connectionrequests.objects.filter(
            Q(sender=request.user.profile) | Q(receiver=request.user.profile)
        ).values_list('sender_id', 'receiver_id')  # Fetch sender and receiver IDs as a tuple

        # Flatten the tuple into a single list of IDs
        connected_ids = set([item for sublist in existing_connections for item in sublist])

        profiles = Profile.objects.exclude(user=request.user).exclude(
            id__in=connected_ids
        ).exclude(
            user__is_staff=True  # Exclude admin/staff users
        )

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

    # Create a unique room name or slug based on the users
    room_name = f"Chatroom for {connection_request.sender.user.username} and {connection_request.receiver.user.username}"
    room_slug = room_name.replace(" ", "-").lower()

    # Check if the room already exists to avoid duplicates
    room, created = Room.objects.get_or_create(name=room_name, slug=room_slug)

    # Save the reference to the room in the connection request
    connection_request.chatroomname = room.slug  # or use room.id if preferred
    connection_request.save()

    print("Room created:", room.name)
    return redirect('viewmyconnectionrequests')

    connection_request.chatroomname = "Chatroom for "+ connection_request.sender.user.username +" and "+connection_request.receiver.user.username
    connection_request.save()

    
    
    return redirect('viewmyconnectionrequests')  # Redirect back to the list of requests

@login_required
def reject_connection_request(request, request_id):
    connection_request = get_object_or_404(Connectionrequests, id=request_id, receiver=request.user.profile)
    connection_request.delete()
    
    return redirect('viewmyconnectionrequests')  # Redirect back to the list of requests



@login_required
def send_message(request, room_name):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        username = request.user.username

        # Create a new message and save it to the database
        new_message = Message.objects.create(
            room=room_name,
            username=username,
            message_content=message_content,
        )
        new_message.save()

    return redirect('chat-room', room_name=room_name)


# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
import os

@csrf_exempt
def upload_file(request, room_name):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        message_content = request.POST.get('message', '')

        # Save message with the file
        message = Message.objects.create(
            room=room_name,
            username=request.user.username,
            message_content=message_content,
            file=uploaded_file
        )

        return JsonResponse({'file_url': message.file.url})

    return JsonResponse({'error': 'Invalid request'}, status=400)
