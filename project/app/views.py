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
    providers = ServiceProvider.objects.all()
    return render(req,'admin/home.html',{'providers':providers})



def category(req):
    if req.method == 'POST':
        category_name = req.POST['category']
        img = req.FILES.get('img') 

        if category_name and img: 
            Category.objects.create(category=category_name, img=img)
            return redirect(view_category)
        return render(req, 'admin/category.html', {'error': 'Both category name and image are required.'})

    return render(req, 'admin/category.html')


def view_category(req):
    category=Category.objects.all()
    return render(req,'admin/view_category.html',{'category':category})


def delete_category(req,id):
    data=Category.objects.get(pk=id)
    data.delete()
    return redirect(view_category)

def add_pro(req):
    categories = Category.objects.all()
    if req.method == "POST":
        category = Category.objects.get(id=req.POST['category'])
        profile = req.FILES.get("profile")
        name = req.POST.get("name")
        phone = req.POST.get("phone")
        experience = req.POST.get("experience")
        availability = req.POST.get("availability") == "on"
        rating = req.POST.get("rating", 0.0)
        location = req.POST.get("location")
        des = req.POST.get("des")
        charge = req.POST.get("charge")
        working_hours = req.POST.get("working_hours")
        
        
        ServiceProvider.objects.create(
            category=category,
            profile=profile,
            name=name,
            phone=phone,
            experience=experience,
            availability=availability,
            rating=rating,
            location=location,
            des=des,
            charge=charge,
            working_hours=working_hours,
        )
        return redirect(admin_home)
    else:
        categories = Category.objects.all()
        return render(req, "admin/add_pro.html", {"categories": categories})
    
def edit_pro(req, pid):
    try:
        provider = ServiceProvider.objects.get(id=pid)
    except ServiceProvider.DoesNotExist:
       
        return redirect('error_page') 
    categories = Category.objects.all()
    
    if req.method == "POST":
        category = Category.objects.get(id=req.POST['category'])
        profile = req.FILES.get("profile", provider.profile) 
        name = req.POST.get("name", provider.name)
        phone = req.POST.get("phone", provider.phone)
        experience = req.POST.get("experience", provider.experience)
        availability = req.POST.get("availability", "on") == "on"  
        rating = req.POST.get("rating", provider.rating)  
        location = req.POST.get("location", provider.location)
        des = req.POST.get("des", provider.des)
        charge = req.POST.get("charge", provider.charge)
        working_hours = req.POST.get("working_hours", provider.working_hours)
        
        provider.category = category
        provider.profile = profile
        provider.name = name
        provider.phone = phone
        provider.experience = experience
        provider.availability = availability
        provider.rating = rating
        provider.location = location
        provider.des = des
        provider.charge = charge
        provider.working_hours = working_hours
        provider.save()        
        return redirect('admin_home') 
    
    else:
        return render(req, "admin/edit_pro.html", {"provider": provider, "categories": categories})


# ---------------------user----------------------------

def user_home(req):

    return render(req,'user/home.html')

