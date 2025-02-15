from django.shortcuts import render,redirect

# Create your views here.

def login(req):

    return render(req,'login.html')

def home(req):

    return render(req,'dummy_home.html')