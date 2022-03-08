import cgi
import pathlib
from turtle import up
from django.shortcuts import render
from django.http import HttpResponse,  FileResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage #for uploading images
from django.urls import reverse
from django.core import serializers
# from home.models import customer_report as report
from home.forms import CustomerRegisterForm
from home.forms import UpscaleInformation
from home.forms import ModelInformation
from home.models import ModelInfo

import requests
import base64
from PIL import Image
import numpy
import numpy as np
import zipfile # used for zipping
import os # used for get the files and checking what type
import shutil # used for zipping
from pathlib import Path # Finds name of an image file

# import aiohttp, asyncio



# ---------------------------Login Stuff Below-------------------------------------
# Signing up page
def signupPage(request):

    # If the user is already logged in and they try to go back to login page, send them to homepage
    if request.user.is_authenticated:
        return redirect('upload')        

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
            return redirect('upload')
        else:
           messages.error(request, 'Password does not match')

    return render(request, 'signup.html', {'form':form})
    

def loginPage(request):

    # If the user is already logged in and they try to go back to login page, send them to homepage
    if request.user.is_authenticated:
        return redirect('upload')

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
            return redirect('upload')
        else:
            messages.error(request, 'Username OR Password does not exist')

    return render(request, 'login.html')


# Logout the Customer
@login_required(login_url="login")
def logoutUser(request):
    logout(request)
    return redirect('upload')

# -------------------------------------------------------------------------------


# ------------------------Download, sending and ziping files---------------------------
# Sending image to the SISR website
def sendImage(request, image, scaleAmount, modelName, qualityMeasure):
    #### Get the extension of the file ####
    extension = image[1:len(image)].split(".", 1)[1]
    print(extension)

    with open(image,'rb') as binary_file:
        binary_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_data)
        image_message = base64_encoded_data.decode('utf-8')

    baseName = Path(image).stem
    payload = {'type': 'singleImage', 'model': modelName, 'filename': baseName,  'scaleAmount': scaleAmount, 'qualityMeasure': qualityMeasure}
    req = requests.post('http://host.docker.internal:5000/', data=image_message, params=payload)

    return HttpResponse(req.text)


# Initially sending the received zip folder to the SISR website
def sendZip(request, zipfile, scaleAmount, modelName, qualityMeasure):
    fsock = open(zipfile, 'rb')

    payload = {'type': 'zip', 'model': modelName, 'scaleAmount': scaleAmount, 'qualityMeasure': qualityMeasure}
    req = requests.post('http://host.docker.internal:5000/', data=fsock, params=payload)

    return render(request, 'upload.html')


# Download upscaled zipped file received from the SISR website
def downloadZip(request):
    """Download file from url to directory

    URL is expected to have a Content-Disposition header telling us what
    filename to use.

    Returns filename of downloaded file.

    """

    context = {}

    directory = "./"
    response = requests.post('http://host.docker.internal:5000/downloadZip', stream=True)

    
    params = cgi.parse_header(
    response.headers.get('Content-Disposition', ''))[-1]
    if 'filename' not in params:
        raise ValueError('Could not find a filename')

    filename = os.path.basename(params['filename'])
    abs_path = os.path.join(directory, filename)
    with open(abs_path, 'wb') as target:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, target)

    zipPath = "./"+filename
    
    # extract the images from the zip
    with zipfile.ZipFile(zipPath, 'r') as zip_ref:
        zippedFiles = zip_ref.namelist()
        if len(zippedFiles)==1:
            
            # Create directory if it doesn't exist
            if not os.path.isdir("./images/upscaledImages"):
                os.mkdir("./images/upscaledImages")

            zip_ref.extractall("./images/upscaledImages")

    # Get the newly upscaled image
    upscaled = None
    original = None
    if os.path.exists("./images"):
        for file_in_main in os.listdir("./images"):
            if os.path.isfile("./images/"+file_in_main): # item is a file
                try:
                    original = "/images/" + file_in_main
                except OSError as e:
                    print("Error: %s : %s" % ("./images/"+file_in_main, e.strerror))

    if os.path.exists("./images/upscaledImages"):
        for file_in_main in os.listdir("./images/upscaledImages"):
            if os.path.isfile("./images/upscaledImages/"+file_in_main): # item is a file
                try:
                    upscaled = "/images/upscaledImages/" + file_in_main
                except OSError as e:
                    print("Error: %s : %s" % ("./images/upscaledImages/"+file_in_main, e.strerror))
    
    context['original'] = original
    context['upscaled'] = upscaled
            
    return render(request,'download.html', context)


# Send back the upscaled zip folder to user
def sendBackZip(request):
    file_server = pathlib.Path('./upscaledZip.zip')
    if not file_server.exists():
        messages.error(request, 'file not found.')
    else:
        file_to_download = open(str(file_server), 'rb')
        os.remove("./upscaledZip.zip")
        response = FileResponse(file_to_download, content_type='application/force-download')
        response['Content-Disposition'] = 'inline; filename="upscaledZip.zip"'
        cleanDirectories()
        return response


# redirect the user back to the upload page while clearing folders
def backhome(request):
    cleanDirectories()
    return redirect('upload')


# Upload image to the website
def upload(request):
    # Get the database information for the models
    model_list = ModelInfo.objects.all()
    # Put it in a json so that we can code the options in the javascript code
    json_serializer = serializers.get_serializer("json")()
    model_list_js = json_serializer.serialize(model_list, ensure_ascii=False)

    if request.method == 'POST' and request.FILES['upload']:
        

        # Get the form information and uploaded content
        upload = request.FILES['upload']
        # Send POST data to the UpscaleInformation
        form = UpscaleInformation(request.POST)

        # If the form inputs are valid save the user and login them in and send them to the homepage
        # Else display an error
        if form.is_valid():
            scaleAmount = request.POST.get('scaleAmount')
            modelDesc = request.POST.get('model') # This value is the description
            # Map the description to the filename so back end can work with it
            for model in model_list:
                if model.modelDesc == modelDesc:
                    modelName = model.modelfilename
            qualityMeasure = request.POST.get('quality')
            print("Scale:", scaleAmount, ", Model:", modelDesc, ", ModelFileName:", modelName, ", Quality Measure?:", qualityMeasure)
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
            # unzip the file and check image size and type for each image #
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

                # checking if it is a file
                elif os.path.isfile(f): # item is a file
                    # check the extension, if jpeg, png, tiff, or bmp accept
                    extension = filename[1:len(filename)].split(".", 1)[1]
                    accepted_types = ["jpeg", "png", "tiff", "bmp"]

                    if extension in accepted_types:

                        if check_image_size(request,f):
                            print(filename)

                        else:
                            # delete that file so that we can zip the valid files
                            try:
                                os.remove("./images/extractedImages/"+filename)
                            except OSError as e:
                                print("Error: %s : %s" % ("./images/extractedImages/"+filename, e.strerror))

                    else:
                        print("Error (file not correct type):", filename, "does not meet the requirements to upscale and therefore will not be processed.")
                        # delete that file so that we can zip the valid files
                        try:
                            os.remove("./images/extractedImages/"+filename)
                        except OSError as e:
                            print("Error: %s : %s" % ("./images/extractedImages/"+filename, e.strerror))

                else:
                    continue # do not do anything with it

            ######################################################
            # Zip all the images that meet the size and type requirement #
            ######################################################
            shutil.make_archive("./images/validZip", 'zip', "./images/extractedImages")
            file_url = "/images/validZip.zip"

            ######################################################
            # Send the zip file to the backend server #
            ######################################################
            sendZip(request, "."+file_url, scaleAmount, modelName, qualityMeasure) #"./images/"+upload.name
            cleanDirectories()
            return redirect('downloadZip')

        else: # the uploaded file was a single image

            # Check if the uploaded image is valid size/resolution
            if check_image_size(request, upload):
                fss = FileSystemStorage()
                # Save the image to the images folder
                file = fss.save(upload.name, upload)
                file_url = fss.url(file) # Get the location of the file with just uploaded and saved
 
                ##### Send the image to the backend server #####
                sendImage(request, "."+file_url, scaleAmount, modelName, qualityMeasure) #"./images/"+upload.name
                return redirect('downloadZip')

    return render(request, 'upload.html', {'model_list': model_list, 'model_list_js':model_list_js})


# Sending model to the SISR website
def sendModel(request, modelfile, modelDesc):
    payload = {'modelDesc': modelDesc, 'filename': modelfile.name}
    req = requests.post('http://host.docker.internal:5000/uploadModel', data=modelfile, params=payload)
    return HttpResponse(req.text)


# Upload model to the website
def uploadModel(request):

    if request.method == 'POST':
        upload = request.FILES['upload_model']

        # Send POST data to the UpscaleInformation
        form = ModelInformation(request.POST, request.FILES)
        # print("Model Name:", upload.name)
        if form.is_valid():
            modelDesc = request.POST.get('modelDesc')
            # upload = request.FILES['upload_model']#.get('model')
            modelfilename = upload.name
            ### Update and add the information to the database ###
            m = ModelInfo(modelDesc=modelDesc, modelfilename=modelfilename)
            m.save()

        ##### Send the image to the backend server #####
        sendModel(request, upload, modelDesc)

        return render(request, 'model_upload.html')
    else:
        form = ModelInformation()
    return render(request, 'model_upload.html', {'form': form})


# Remove/delete the files in the images and extractedImages folders
def cleanDirectories():
    ####################################
    # Delete the items in subdirectory #
    ####################################
    if os.path.exists("./images/extractedImages"):
        for file_in_sub in os.listdir("./images/extractedImages"):
            if os.path.isdir("./images/extractedImages/"+file_in_sub):
                try:
                    shutil.rmtree("./images/extractedImages/"+file_in_sub)
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
    if os.path.exists("./images"):
        for file_in_main in os.listdir("./images"):
            if os.path.isdir("./images/"+file_in_main): # item is a directory
                continue # do not delete
            elif os.path.isfile("./images/"+file_in_main): # item is a file
                try:
                    os.remove("./images/"+file_in_main)
                except OSError as e:
                    print("Error: %s : %s" % ("./images/"+file_in_main, e.strerror))
    
    if os.path.exists("./images/upscaledImages"):
        for file_in_sub in os.listdir("./images/upscaledImages"):
            if os.path.isdir("./images/upscaledImages/"+file_in_sub):
                try:
                    shutil.rmtree("./images/upscaledImages/"+file_in_sub)
                except OSError as e:
                    print("Error: %s : %s" % ("./images/upscaledImages/"+file_in_sub, e.strerror))
            else:
                try:
                    os.remove("./images/upscaledImages/"+file_in_sub)
                except OSError as e:
                    print("Error: %s : %s" % ("./images/upscaledImages/"+file_in_sub, e.strerror))

# -------------------------------------------------------------------------------


# ---------------------------Helper methods-------------------------------------
def check_image_size(request, image):
    img= Image.open(image).convert('L') # open the saved image that the user uploaded and convert it to 2D from 3D
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

