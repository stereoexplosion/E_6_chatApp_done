from django.contrib import admin

from .models import *

admin.site.register(Message)
admin.site.register(ProfilePhoto)
admin.site.register(GroupMessage)
admin.site.register(GroupChat)
admin.site.register(GroupChatUser)
