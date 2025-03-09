from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from .models import Friends, Messages
from .serializers import MessageSerializer
from django.db.models import Q

User = get_user_model()

def getFriendsList(id):
    try:
        user = User.objects.get(id=id)
        ids = list(user.friends_set.all())
        friends = []
        for id in ids:
            num = str(id)
            fr = User.objects.get(id=int(num))
            friends.append(fr)
        return friends
    except:
        return []

def getUserId(username):
    use = User.objects.get(username=username)
    id = use.id
    return id

def index(request):
    if not request.user.is_authenticated:
        print("Not Logged In!")
        return render(request, "chat/index.html", {})
    else:
        username = request.user.username
        id = getUserId(username)
        friends = getFriendsList(id)
        return render(request, "chat/Base.html", {'friends': friends})

def search(request):
    users = list(User.objects.all())
    for user in users:
        if user.username == request.user.username:
            users.remove(user)
            break

    if request.method == "POST":
        print("SEARCHING!!")
        query = request.POST.get("search")
        user_ls = []
        for user in users:
            if query in user.name or query in user.username:
                user_ls.append(user)
        return render(request, "chat/search.html", {'users': user_ls, })

    try:
        users = users[:10]
    except:
        users = users[:]
    id = getUserId(request.user.username)
    friends = getFriendsList(id)
    return render(request, "chat/search.html", {'users': users, 'friends': friends})
def addFriend(request, name):
    username = request.user.username
    id = getUserId(username)
    friend = User.objects.get(username=name)
    curr_user = User.objects.get(id=id)

    ls = curr_user.friends_set.all()
    flag = 0
    for username in ls:
        if username.friend == friend.id:
            flag = 1
            break
    if flag == 0:
        print("Friend Added!!")
        curr_user.friends_set.create(friend=friend.id)
        friend.friends_set.create(friend=id)
    return redirect("search")  # Use the URL name instead of hardcoded path

def search(request):
    users = list(User.objects.all())
    for user in users:
        if user.username == request.user.username:
            users.remove(user)
            break

    if request.method == "POST":
        print("SEARCHING!!")
        query = request.POST.get("search")
        user_ls = []
        for user in users:
            if query.lower() in user.username.lower():
                user_ls.append(user)
        return render(request, "chat/search.html", {'users': user_ls})

    # GET request handling
    try:
        users = users[:10]
    except:
        users = users[:]

    id = getUserId(request.user.username)
    friends = getFriendsList(id)
    return render(request, "chat/search.html", {'users': users, 'friends': friends})

User = get_user_model()

def chat(request, username):
    friend = User.objects.get(username=username)
    curr_user = request.user  # Simplify this since request.user is already the User object

    # Get only parent messages first
    messages = Messages.objects.filter(
        parent=None
    ).filter(
        Q(sender_name=curr_user, receiver_name=friend) |
        Q(sender_name=friend, receiver_name=curr_user)
    ).prefetch_related('replies')

    if request.method == "GET":
        friends = getFriendsList(curr_user.id)
        return render(request, "chat/messages.html",
                    {'messages': messages,
                     'friends': friends,
                     'curr_user': curr_user,
                     'friend': friend})
@csrf_exempt
def message_list(request, sender=None, receiver=None):
    if request.method == 'GET':
        messages = Messages.objects.filter(sender_name=sender, receiver_name=receiver, seen=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.seen = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)