import email
import imp
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.forms import ModelForm, TextInput, EmailInput, PasswordInput

from home.models import Info
from home.models import ModelInfo

# Form structure

class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class UpscaleInformation(forms.Form):
    class Meta:
        model = Info
        fields = ['image', 'scaleAmount', 'model', 'qualityMeasure']

class ModelInformation(forms.Form):
    # model = forms.FileField()
    # modelDesc = forms.CharField(max_length=20, required=True, help_text='Required.')
    # modelfilename = forms.CharField(max_length=255, required=False, help_text='Optional.')
    class Meta:
        model = ModelInfo
        fields = ['modelDesc', 'model']