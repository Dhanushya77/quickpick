from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from.models import *
import os
from django.contrib.auth.models import User
# Create your views here.

def user_login(req):
    if 'admin' in req.session:
        return redirect (admin_home)
    if 'user' in req.session:
        return redirect(user_home)
    if req.method == 'POST':
        uname = req.POST['uname']
        password = req.POST['password']
        admin = authenticate(username=uname,password=password)
        if admin:
            login(req,admin)
            if admin.is_superuser:
                req.session['admin'] = uname
                return redirect(admin_home)
            else:
                req.session['user'] = uname
                return redirect(user_home)
        else:
            messages.warning(req,'Invalid username or password')
            return redirect(user_login)
    else:
        return render(req,'login.html')
    

def user_logout(req):
    if 'user' or 'admin' in req.session:
        logout(req)
        req.session.flush()
        return redirect(user_login)
    else:
        return redirect(user_login)
    
def dummy_home(req):

    return render(req,'dummy_home.html')


# --------------------admin----------------------------

def admin_home(req):

    return render(req,'admin/home.html')

def category(req):
    if req.method=='POST':
        category=req.POST['category']
        img=req.file.get('img')
        data= Category.objects.create(category=category,img=img)
        data.save()
        return redirect(view_category)
    else:
        data=Category.objects.all()
        return render(req,'admin/category.html',{'data':data})


def view_category(req):
    category=Category.objects.all()
    return render(req,'admin/view_category.html',{'category':category})


def delete_category(req,id):
    data=Category.objects.get(pk=id)
    data.delete()
    return redirect(view_category)


#-----------------service providers--------------------
def service_home(req):

    return render(req,'service/home.html')

# ---------------------user----------------------------

def user_home(req):

    return render(req,'user/home.html')

