import email
import imp
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.forms import ModelForm, TextInput, EmailInput, PasswordInput

# Form structure

class CustomerRegisterForm(UserCreationForm):
    username = forms.CharField(required=True,max_length=100,help_text='100 characters max')
    email = forms.EmailField(required=True,help_text='valid email address is required')
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username', 'style': 'width: 300px;'}))
    last_name = forms.CharField(widget=TextInput(attrs={'placeholder': 'Last Name', 'style': 'width: 300px;'}))
    email = forms.EmailField(widget=EmailInput(attrs={'placeholder' :'Email', 'style': 'width: 300px;'}))
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username', 'style': 'width: 300px;'}))
    password1 = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password', 'type':'password', 'style': 'width: 300px;'}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Confirm Password', 'type':'password', 'style': 'width: 300px;'}))
    class Meta:
        model = User
        fields = ("username","email","password1","password2")