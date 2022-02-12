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
from PIL import Image
import numpy
import cv2
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
def sendImage(request, image):
    #### Get the extension of the file ####
    extension = image[1:len(image)].split(".", 1)[1]
    # print(extension)
    content_type = 'image/' + extension
    headers = {'content-type': content_type}

    img = cv2.imread(image)
    # encode image as png
    _, img_encoded = cv2.imencode('.png', img)
    # send http request with image and receive response
    req = requests.post('http://host.docker.internal:5000/', data=img_encoded.tostring(), headers=headers)


    # files = {'media': open(image, 'rb')}
    # req = requests.post('http://host.docker.internal:5000/', files=files)
    return HttpResponse(req.text)

# Upload image to the website
def upload(request):
    if request.method == 'POST' and request.FILES['upload']:
        upload = request.FILES['upload']
        # Check if the uploaded image is valid size/resolution
        if check_image_size(request, upload):
            fss = FileSystemStorage()
            # Save the image to the images folder
            file = fss.save(upload.name, upload)
            file_url = fss.url(file) # Get the location of the file with just uploaded and saved
            # print(file_url)

            ##### Send the image to the backend server #####
            sendImage(request, "."+file_url) #"./images/"+upload.name
            return render(request, 'upload.html', {'file_url': file_url})
    return render(request, 'upload.html')

def test_connection(request):
    # return HttpResponse("TESTING")
    req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return HttpResponse(req.text)

def check_image_size(request, image):
    img= Image.open(image) # open the saved image that the user uploaded
    np_img = numpy.array(img) #convert to a numpy array
    height, width, size = np_img.shape
    
    # Check the resolution of the image and make sure it is within the requirements of 128-1080 pixels by 128-1080 pixels
    if height < 128 or width < 128:
        print('Image size is too small to upscale.')
        messages.error(request, 'Image size is too small to upscale.')
        return False
    if height > 1080 or width > 1080:
        print('Image size is too large to upscale.')
        messages.error(request, 'Image size is too large to upscale.')
        return False
    
    return True