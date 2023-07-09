from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import TextInput

from .models import ProfilePhoto, GroupChat


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ('photo',)


class ChangeNickname(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
        }


class GroupChatCreateForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ['group_chat_title', 'photo_chat']



