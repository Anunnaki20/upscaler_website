from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

import requests
def test_connection(request):
    # return HttpResponse("TESTING")
    req = requests.post('http://host.docker.internal:5000/', json={"data": "Hello"})
    return HttpResponse(req.text)