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
from django.urls import reverse
# from home.models import customer_report as report
from home.forms import CustomerRegisterForm
from home.forms import UpscaleInformation

import requests
from PIL import Image
import numpy
import cv2
import numpy as np
import zipfile # used for zipping
import os # used for get the files and checking what type
import shutil # used for zipping
import mimetypes # used for downloading link
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
def sendImage(request, image, scaleAmount, modelName, qualityMeasure):
    #### Get the extension of the file ####
    # extension = image[1:len(image)].split(".", 1)[1]
    # print(extension)
    # content_type = 'image/' + extension
    # headers = {'content-type': content_type}

    img = cv2.imread(image)
    # encode image as png
    _, img_encoded = cv2.imencode('.png', img)
    # send http request with image and receive response
    imagearr = img_encoded.tostring()

    payload = {'type': 'singleImage', 'model': modelName, 'scaleAmount': scaleAmount, 'qualityMeasure': qualityMeasure}
    req = requests.post('http://host.docker.internal:5000/', data=imagearr, params=payload)

    return HttpResponse(req.text)


# Sending zip file to the SISR website
def sendZip(request, zipfile, scaleAmount, modelName, qualityMeasure):
    content_type = 'application/zip'
    headers = {'content-type': content_type}

    fsock = open(zipfile, 'rb')

    payload = {'type': 'zip', 'model': modelName, 'scaleAmount': scaleAmount, 'qualityMeasure': qualityMeasure}
    req = requests.post('http://host.docker.internal:5000/', data=fsock, params=payload)

    return HttpResponse(req.text)


# Upload image to the website
def upload(request):
    if request.method == 'POST' and request.FILES['upload']:
        upload = request.FILES['upload']

        # Send POST data to the UpscaleInformation
        form = UpscaleInformation(request.POST)

        # If the form inputs are valid save the user and login them in and send them to the homepage
        # Else display an error
        if form.is_valid():
            scaleAmount = request.POST.get('scaleAmount')
            modelName = request.POST.get('model')
            qualityMeasure = request.POST.get('quality')
            print("Scale:", scaleAmount, ", Model:", modelName, ", Quality Measure?:", qualityMeasure)
            # return render(request, 'info.html')

        # If it is then we will want to run a different function to handle the zip
        #### Get the extension of the file ####
        extension = upload.name[1:len(upload.name)].split(".", 1)[1]
        print(extension)

        # Check if the uploaded file is .zip
        if extension == "zip":
            fss = FileSystemStorage()
            # Save the zip file to the images folder
            file = fss.save(upload.name, upload)
            file_url = fss.url(file) # Get the location of the file with just uploaded and saved

            ######################################################
            # unzip the file and check image size for each image #
            ######################################################
            # extract the images from the zip
            with zipfile.ZipFile("."+file_url, 'r') as zip_ref:
                zip_ref.extractall("./images/extractedImages")

            # check if each item in the extracted zip are of accepted extension types
            for filename in os.listdir("./images/extractedImages"):
                f = os.path.join("./images/extractedImages", filename)
                if os.path.isdir(f): # item is a directory
                    print("Error (folder in zip):", filename, "does not meet the requirements to upscale and therefore will not be processed.")
                    # delete that folder so that we can zip the valid files
                    try:
                        shutil.rmtree("./images/extractedImages/"+filename)
                    except OSError as e:
                        print("Error: %s : %s" % ("./images/extractedImages/"+filename, e.strerror))
                    continue # do not do anything with it
                # chekcing if it is a file
                elif os.path.isfile(f): # item is a file
                    # check the extension, if jpeg, png, tiff, or bmp accept
                    extension = filename[1:len(filename)].split(".", 1)[1]
                    accepted_types = ["jpeg", "png", "tiff", "bmp"]
                    if extension in accepted_types:
                        print(filename)
                    else:
                        print("Error (file not correct type):", filename, "does not meet the requirements to upscale and therefore will not be processed.")
                        # delete that file so that we can zip the valid files
                        try:
                            os.remove("./images/extractedImages/"+filename)
                        except OSError as e:
                            print("Error: %s : %s" % ("./images/extractedImages/"+filename, e.strerror))
                    # print(f, "filename:", filename)
                else:
                    continue # do not do anything with it

            ######################################################
            # Zip all the images that meet the size requirement #
            ######################################################
            shutil.make_archive("./images/validZip", 'zip', "./images/extractedImages")
            file_url = "/images/validZip.zip"

            ######################################################
            # Send the zip file to the backend server #
            ######################################################
            ##### Send the zip file to the backend server #####
            sendZip(request, "."+file_url, scaleAmount, modelName, qualityMeasure) #"./images/"+upload.name
            return render(request, 'upload.html')

        else: # the uploaded file was a single image
            # Check if the uploaded image is valid size/resolution
            if check_image_size(request, upload):
                fss = FileSystemStorage()
                # Save the image to the images folder
                file = fss.save(upload.name, upload)
                file_url = fss.url(file) # Get the location of the file with just uploaded and saved
                # print(file_url)

                ##### Send the image to the backend server #####
                sendImage(request, "."+file_url, scaleAmount, modelName, qualityMeasure) #"./images/"+upload.name
                return render(request, 'upload.html', {'file_url': file_url})
    return render(request, 'upload.html')

# Remove/delete the files in the images and extractedImages folders
def cleanDirectories(request):
    ####################################
    # Delete the items in subdirectory #
    ####################################
    for file_in_sub in os.listdir("./images/extractedImages"):
        if os.path.isdir("./images/extractedImages/"+file_in_sub):
            try:
                shutil.rmtree("./images/extractedImages/"+file_in_sub)
                # os.rmdir("./images/extractedImages/"+file_in_sub)
            except OSError as e:
                print("Error: %s : %s" % ("./images/extractedImages/"+file_in_sub, e.strerror))
        else:
            try:
                os.remove("./images/extractedImages/"+file_in_sub)
            except OSError as e:
                print("Error: %s : %s" % ("./images/extractedImages/"+file_in_sub, e.strerror))

    ########################################
    # Delete the items in images directory #
    ########################################
    for file_in_main in os.listdir("./images"):
        if os.path.isdir("./images/"+file_in_main): # item is a directory
            continue # do not delete
        elif os.path.isfile("./images/"+file_in_main): # item is a file
            try:
                os.remove("./images/"+file_in_main)
            except OSError as e:
                print("Error: %s : %s" % ("./images/"+file_in_main, e.strerror))
    
    return render(request, 'clean.html')

# Get the zip file from the backend
def getUpscaled(request):
    # handle the POST request
    if request.method == 'POST':

        # r = request
        file_content = requests.get('http://host.docker.internal:5000/')
        # parameters = r.params
        # print(r.args)
        # Assign the parameters to their own variables
        # singleImage = parameters['single'] # if False then not single image, if True then only one image in zip
        # filetype = parameters['type']
        # scale = parameters['scaleAmount']
        # model = parameters['model']
        # qualityMeasure = parameters['qualityMeasure']
        # print("File Type:", filetype, ", Scale:", scale, ", Model:", model, ", Quality Measure?:", qualityMeasure)
        # print("Single Image?:", singleImage)

        # if filetype == "zip":
        zip_result = open('./images/upscaledImages/results.zip', 'wb')
        zip_result.write(file_content.content)
        # zip_result.write(request.data)

        #########################################
        # unzip the file if single image in zip #
        #########################################
        # if singleImage:
        file_url = "/images/upscaledImages/results.zip"
        # extract the image from the zip to display
        with zipfile.ZipFile("."+file_url, 'r') as zip_ref:
            zip_ref.extractall("./upscaledImages/")

        file_url = "/upscaledImages/test.png"
        
        return HttpResponse(file_content.text)
        # return render(request, 'testing.html', {'file_url': file_url})
        # return


# Render the download website
def download(request):
    return render(request, 'download.html')

# Downloadable link
def download_file(request): #, filename=''
    ######################################################################################################
    # Current code doesn't allow you to click a link, instead it just automatically asks to save or open #
    ######################################################################################################

    # if filename != '':
    # Define file name
    filename = '56364398.png'
    # filename = "results.zip"
    # filename = 'validZip.zip'
    # filename = 'upscaled.zip'
    # Define the full file path
    # filepath = "./images/upscaledImages/upscaled.zip"
    # filepath = "./images/upscaledImages/results.zip"
    filepath = "./images/upscaledImages/56364398.png"
    # filepath = "./images/validZip.zip"
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response



def test_connection(request):
    # return HttpResponse("TESTING")
    req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return HttpResponse(req.text)

def check_image_size(request, image):
    img= Image.open(image) # open the saved image that the user uploaded
    np_img = numpy.array(img) #convert to a numpy array
    height, width = np_img.shape
    
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