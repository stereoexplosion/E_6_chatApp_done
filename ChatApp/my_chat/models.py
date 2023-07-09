from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'


class GroupChat(models.Model):
    members = models.ManyToManyField(User, through='GroupChatUser', related_name='members')
    chat_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_author')
    group_chat_title = models.CharField(max_length=64)
    photo_chat = models.ImageField(upload_to='group_chat_avatars', default='default_avatar/default.jpg')

    def __str__(self):
        return self.group_chat_title

    class Meta:
        verbose_name = 'Групповой чат'
        verbose_name_plural = 'Групповые чаты'

    def get_absolute_url(self):
        return reverse('group_chat', args=[str(self.id)])


class GroupChatUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE)


class GroupMessage(models.Model):
    group_chat = models.ForeignKey(GroupChat, related_name='chat', on_delete=models.CASCADE)
    group_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_sender', null=True, blank=True)
    group_message = models.CharField(max_length=1200)
    group_timestamp = models.DateTimeField(auto_now_add=True)
    group_is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.group_message

    class Meta:
        ordering = ('group_timestamp',)
        verbose_name = 'Сообшение группового чата'
        verbose_name_plural = 'Сообщения групповых чатов'


class ProfilePhoto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='avatars', default='default_avatar/default.jpg')

    def __str__(self):
        return User.objects.get(id=self.user_id).username

    class Meta:
        verbose_name = 'Фото автара'
        verbose_name_plural = 'Фотографии для аватаров'
