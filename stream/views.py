from django.shortcuts import render, HttpResponse

# Create your views here.

def stream(request):
    return HttpResponse("Stream app installed")