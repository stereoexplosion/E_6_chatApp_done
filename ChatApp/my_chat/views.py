from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import CreateView, DeleteView, UpdateView
from rest_framework.parsers import JSONParser

from .models import Message, ProfilePhoto, GroupMessage, GroupChat, GroupChatUser
from .forms import SignUpForm, ImageForm, ChangeNickname, GroupChatCreateForm
from .serializers import MessageSerializer, UserSerializer, GroupChatSerializer


@csrf_protect
def index(request):
    if request.user.is_authenticated:
        return redirect('chats')
    if request.method == 'GET':
        return render(request, 'chat/index.html', {})
    if request.method == "POST":
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse('{"error": "User does not exist"}')
        return redirect('chats')


@csrf_exempt
def message_list(request, sender=None, receiver=None):
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    ProfilePhoto.objects.create(user=request.user)
                    return redirect('chats')
    else:
        form = SignUpForm()
    template = 'chat/register.html'
    context = {'form': form}
    return render(request, template, context)


@csrf_protect
def chat_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        return render(request, 'chat/chat.html',
                      {'users': User.objects.exclude(username=request.user.username).exclude(username='admin')})


@csrf_protect
def message_view(request, sender, receiver):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        return render(request, "chat/messages.html",
                      {'users': User.objects.exclude(username=request.user.username).exclude(username='admin'),
                       'receiver': User.objects.get(id=receiver),
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                   Message.objects.filter(sender_id=receiver, receiver_id=sender)})


@csrf_protect
def logout_view(request):
    logout(request)
    return redirect('index')


@csrf_protect
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        action = request.POST.get('change')
        if action == 'photo':
            old_photo = ProfilePhoto.objects.get(user_id=request.user.id)
            form_photo = ImageForm(request.POST, request.FILES, instance=old_photo)
            form_nick = ChangeNickname()
            if form_photo.is_valid():
                form_photo.save()
                return redirect('profile_view')
        elif action == 'nickname':
            old_nickname = User.objects.get(id=request.user.id)
            form_nick = ChangeNickname(request.POST, instance=old_nickname)
            form_photo = ImageForm()
            if form_nick.is_valid():
                form_nick.save()
                return redirect('profile_view')
    else:
        form_nick = ChangeNickname()
        form_photo = ImageForm()
    return render(request, 'chat/profile.html', {'form_photo': form_photo, 'form_nick': form_nick})


@csrf_protect
def group_chat_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        where_author = [item for item in GroupChat.objects.filter(chat_author=request.user.id)]
        where_user_ = [item.group_chat_id for item in GroupChatUser.objects.filter(user=request.user.id)]
        where_user = []
        for id_ in where_user_:
            where_user.append(GroupChat.objects.get(id=id_))
        return render(request, 'chat/group_chat.html',
                      {'group_chats': where_user + where_author})


@csrf_protect
def group_message_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        where_author = [item for item in GroupChat.objects.filter(chat_author=request.user.id)]
        where_user_ = [item.group_chat_id for item in GroupChatUser.objects.filter(user=request.user.id)]
        where_user = []
        for id_ in where_user_:
            where_user.append(GroupChat.objects.get(id=id_))
        user_id = GroupChatUser.objects.filter(group_chat_id=pk).values_list('user_id', flat=True)
        users_in_chat = []
        for _id in user_id:
            users_in_chat.append(User.objects.get(id=_id))
        author = User.objects.get(id=GroupChat.objects.get(id=pk).chat_author_id).username

        return render(request, "chat/group_messages.html",
                      {'group_chats': where_user + where_author,
                       'chat_id': int(GroupChat.objects.get(id=pk).id),
                       'messages': GroupMessage.objects.filter(group_chat_id=pk),
                       'users_in_chat': users_in_chat,
                       'author': author
                       })


@csrf_exempt
def group_message_list(request, group_chat_id=None, pk=None):
    if request.method == 'GET':
        messages = GroupMessage.objects.filter(group_chat_id=group_chat_id, group_is_read=False)
        serializer = GroupChatSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.group_is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = GroupChatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


class GroupChatCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    form_class = GroupChatCreateForm
    model = GroupChat
    template_name = 'chat/group_chat_create.html'
    success_url = reverse_lazy('group_chats')

    def form_valid(self, form):
        chat = form.save(commit=False)
        chat.chat_author = self.request.user
        return super().form_valid(form)


class GroupChatEdit(LoginRequiredMixin, UpdateView):
    raise_exception = True
    form_class = GroupChatCreateForm
    model = GroupChat
    template_name = 'chat/group_chat_edit.html'


class GroupChatDelete(LoginRequiredMixin, DeleteView):
    raise_exception = True
    model = GroupChat
    template_name = 'chat/group_chat_delete.html'
    success_url = reverse_lazy('group_chats')


@csrf_exempt
def users_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    author = GroupChat.objects.get(id=pk).chat_author_id
    if request.user.id != author:
        return redirect('group_chats')
    user_id = GroupChatUser.objects.filter(group_chat_id=pk).values_list('user_id', flat=True)
    users_in_chat = []
    for _id in user_id:
        users_in_chat.append(User.objects.get(id=_id))
    users_not_in_chat = [item for item in User.objects.all().exclude(username='admin').exclude(username=request.user.username) if item not in users_in_chat]
    if request.method == "POST":
        # add_user = request.POST.get('add_user')
        # delete_user = request.POST.get('delete_user')
        if 'add_user' in request.POST:
            u_id = request.POST.get('add_user')
            GroupChatUser.objects.create(group_chat_id=pk, user_id=u_id)
            return redirect('/group_chat/users/' + str(pk))
        elif 'delete_user' in request.POST:
            u_id = request.POST.get('delete_user')
            GroupChatUser.objects.get(user_id=u_id).delete()
            # GroupChat.objects.filter(group_sender_id=u_id).delete()
            return redirect('/group_chat/users/' + str(pk))

    return render(request, "chat/group_chat_users.html",
                  {
                   'chat': GroupChat.objects.get(id=pk),
                   'users_in_chat': users_in_chat,
                   'users_not_in_chat': users_not_in_chat
                   })

