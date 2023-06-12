from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Topic, Room, Message, User
from .forms import RoomForm, UserForm


def home(request):
    """ Main page """
    topics = Topic.objects.all()[0:4]

    # kod do wyszukiwania 
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    rooms = Room.objects.filter(
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(topic__name__icontains=q)
    )
    room_count = rooms.count()

    # 
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) 
    )[0:6]

    context = {'topics': topics, 'rooms': rooms, 'rooms_count': room_count,
               'room_messages': room_messages,}
    
    return render(request, 'base/home.html', context)


def room(request, pk):
    """ shows details of the room """
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method== 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user) # dodaje uzytkownika do uczestnikow danego pokoju
        return redirect('room', pk=room.id)

    context = {'room': room, 'participants': participants, 'room_messages': room_messages,}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    """ show details of a user"""
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'rooms_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('update-user')
    
    
    context = {'form': form}
    return render(request, 'base/update-user.html', context)


@login_required
def createRoom(request):
    """ create a new room"""
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')

    context = {'topics': topics, 'form': form}
    return render(request, 'base/room-form.html', context)


@login_required
def updateRoom(request, pk):
    """ Update an existing room """
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        messages.error(request, "You are not allowed here! Only room's creater can edit.")
        return redirect('home')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    

    context = {'topics': topics, 'form': form, 'room': room}
    return render(request, 'base/room-form.html', context)


@login_required
def deleteRoom(request, pk):
    """ deleate a room"""
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        messages.error(request, "Only a host can delete a room!")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    
    context = {'obj': room}

    return render(request, 'base/delete.html', context) 


@login_required
def deleteMessage(request, pk):
    """ delete a message"""
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        messages.error(request, "you can't delete a message!")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    

    context = {'obj': message}
    return render(request, 'base/delete.html', context)


def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics': topics}

    return render(request, 'base/topics.html', context)



def activityPage(request):
    all_messages = Message.objects.all()
    context = {'all_messages': all_messages}
    return render(request, 'base/activity.html', context)