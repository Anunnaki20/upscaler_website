import email
import imp
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.forms import ModelForm, TextInput, EmailInput, PasswordInput

from home.models import Info

# Form structure

class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


SCALE_CHOICES = [('double', 'x2'), ('quad', 'x4')]
MODEL_CHOICES = [('model_h5', 'model.5'), ('model_4_t1024_h5', 'model_4_t1024.h5')]

class UpscaleInformation(forms.Form):
    # scaleAmount= forms.CharField(label='Select Scale Factor', widget=forms.RadioSelect(choices=SCALE_CHOICES))
    # model = forms.MultipleChoiceField(
    #     required=True,
    #     widget=forms.CheckboxSelectMultiple,
    #     choices=MODEL_CHOICES,
    # )

    class Meta:
        model = Info
        fields = ['image', 'scaleAmount', 'model']