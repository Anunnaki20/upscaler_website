from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage #for uploading images
# from home.models import customer_report as report
from home.forms import CustomerRegisterForm

import requests
import base64
# Create your views here.


# import requests
def homepage(request):
    # return HttpResponse("TESTING")
    # req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return render(request, 'homepage.html')


# Signing up page
def signupPage(request):        

    form = CustomerRegisterForm()
    if request.method == 'POST':
        # Send POST data to the UserCreationForm
        form = CustomerRegisterForm(request.POST)

        # If the form inputs are valid save the user and login them in and send them to the homepage
        # Else display an error
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('homepage')
        else:
           form = CustomerRegisterForm()

    return render(request, 'signup.html', {'form':form})
    
# ---------------------------Login Stuff Below-------------------------------------

# @login_required(login_url="")
def loginPage(request):
    page = 'login'

    # If the user is already logged in and they try to go back to login page, send them to homepage
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':

        # Get the login form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check to make sure that the user is in the database
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        # authenticate the user and log them in
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Username OR Password does not exist')


    context = {'page' : page}
    return render(request, 'login.html', context)


# Logout the Customer
def logoutCustomer(request):
    logout(request)
    return redirect('login')

# Sending image to the SISR website
def sendImage(request):
    req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return HttpResponse(req.text)

# Upload image to the website
def upload(request):
    if request.method == 'POST' and request.FILES['upload']:
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        return render(request, 'upload.html', {'file_url': file_url})
    return render(request, 'upload.html')

def test_connection(request):
    # return HttpResponse("TESTING")
    req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return HttpResponse(req.text)