from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('chat/', chat_view, name='chats'),
    path('chat/<int:sender>/<int:receiver>/', message_view, name='chat'),
    path('api/messages/<int:sender>/<int:receiver>/', message_list, name='message-detail'),
    path('api/messages/', message_list, name='message-list'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('chat/profile/', profile_view, name='profile_view'),
    path('group_chat/', group_chat_view, name='group_chats'),
    path('group_chat/<int:pk>', group_message_view, name='group_chat'),
    path('api/group_messages/<int:pk>', group_message_list, name='group_message_detail'),
    path('api/group_messages/', group_message_list, name='group_message_list'),
    path('group_chat/create', GroupChatCreate.as_view(), name='group_chat_create'),
    path('group_chat/<int:pk>/edit', GroupChatEdit.as_view(), name='group_chat_edit'),
    path('group_chat/<int:pk>/delete', GroupChatDelete.as_view(), name='group_chat_delete'),
    path('group_chat/users/<int:pk>', users_edit, name='group_chat_users'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


