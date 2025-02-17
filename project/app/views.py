from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from.models import *
import os
from django.contrib.auth.models import User
# Create your views here.

def user_login(req):
    if 'shop' in req.session:
        return redirect (shop_home)
    if 'user' in req.session:
        return redirect(user_home)
    if req.method == 'POST':
        uname = req.POST['uname']
        password = req.POST['password']
        shop = authenticate(username=uname,password=password)
        if shop:
            login(req,shop)
            if shop.is_superuser:
                req.session['shop'] = uname
                return redirect(shop_home)
            else:
                req.session['user'] = uname
                return redirect(user_home)
        else:
            messages.warning(req,'Invalid username or password')
            return redirect(user_login)
    else:
        return render(req,'login.html')
    

def user_logout(req):
    if 'user' or 'shop' in req.session:
        logout(req)
        req.session.flush()
        return redirect(user_login)
    else:
        return redirect(user_login)
    
def dummy_home(req):

    return render(req,'dummy_home.html')


# ----------------------shop--------------------------

def shop_home(req):

    return render(req,'shop/home.html')


# ---------------------user----------------------------

def user_home(req):

    return render(req,'user/home.html')

