from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Message, GroupMessage, GroupChat


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'message', 'timestamp']


class GroupChatSerializer(serializers.ModelSerializer):
    group_chat = serializers.SlugRelatedField(many=False, slug_field='id', queryset=GroupChat.objects.all())
    group_sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())

    class Meta:
        model = GroupMessage
        fields = ['group_chat', 'group_sender', 'group_message', 'group_timestamp']
