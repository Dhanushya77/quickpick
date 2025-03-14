from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from.models import *
import os
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
from django.db.models import Q
from .forms import BookingForm
import razorpay 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


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
    



def user_logout(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            logout(request)
            return redirect(user_login) 
        else:
            
            return HttpResponse("""
                <script type="text/javascript">
                    var confirmation = confirm('Are you sure you want to log out?');
                    if (confirmation) {
                        // Use the URL name for logout here
                        window.location.href = "quick_logout";
                    } else {
                        window.location.href = '/';  // Or wherever you want to redirect
                    }
                </script>
            """)
    else:
        return redirect(user_login) 

def quick_logout(req):
    
    if 'user' or 'admin' in req.session:
        logout(req)
        req.session.flush()
        return redirect(user_login)
    else:
        return redirect(user_login)


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

def view_service(request, cid):
    category = Category.objects.get(id=cid)
    service_providers = ServiceProvider.objects.filter(category=category)
    
    return render(request, 'admin/view_products.html', {
        'category': category,
        'service_providers': service_providers,
    })


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
        if ServiceProvider.objects.filter(phone=phone).exists():
            messages.error(req, "Phone number already exists! Please use a different one.")
            return render(req, "admin/add_pro.html", {"categories": categories})
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
        return redirect(admin_home) 
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
        if ServiceProvider.objects.filter(phone=phone).exists():
            messages.error(req, "Phone number already exists! Please use a different one.")
            return render(req, "admin/edit_pro.html", {"categories": categories})
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
        return redirect(admin_home) 
    
    else:
        return render(req, "admin/edit_pro.html", {"provider": provider, "categories": categories})

def delete_pro(req,pid):
    data=ServiceProvider.objects.get(pk=pid)
    file=data.profile.url
    file=file.split('/')[-1]
    os.remove('media/'+file)
    data.delete()
    return redirect(admin_home)

def admin_bookings(req):
    """ Display pending bookings for the logged-in admin owner """
    if 'admin' in req.session:  
        bookings = Booking.objects.all().order_by('-date')
        return render(req, 'admin/admin_bookings.html', {'bookings': bookings})
    return redirect(user_login)

def confirm_booking(req, booking_id):
    """ Confirm a booking and send an email notification to the user """
    if 'admin' in req.session:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'Confirmed'
        booking.payment_amount = booking.provider.charge * 0.2  
        booking.save()

        try:
            send_mail(
                'Booking Confirmation',
                f'Your booking with {booking.provider.name} on {booking.date} at {booking.time} has been confirmed. Please make an advance payment of {booking.payment_amount}.',
                'your_email@example.com',
                [booking.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}") 

        return redirect(admin_bookings)

    return redirect(user_login)


def decline_booking(req, booking_id):
    """ Decline a booking and notify the user via email """
    if 'admin' in req.session:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'Declined'
        booking.save()

        send_mail(
            'Booking Declined',
            f'Unfortunately, your booking with {booking.provider.name} on {booking.date} at {booking.time} has been declined.',
            'your_email@example.com',
            [booking.user.email],
            fail_silently=False,
        )

        return redirect(admin_bookings)
    return redirect(user_login)

# ---------------------user----------------------------
def register(req):
    if req.method == 'POST':
        uname = req.POST['uname']
        email = req.POST['email']
        pswrd = req.POST['pswrd']
        try:
            data = User.objects.create_user(first_name=uname, email=email, username=email, password=pswrd)
            data.save()
            otp = ""
            for i in range(6):
                otp += str(random.randint(0, 9))
            msg = f'Your registration is completed otp: {otp}'
            otp = Otp.objects.create(user=data, otp=otp)
            otp.save()
            send_mail('Registration', msg, settings.EMAIL_HOST_USER, [email])
            messages.success(req, "Registration successful. Please check your email for OTP.")
            return redirect(otp_confirmation)
        except:
            messages.warning(req, 'Email already exists')
            return redirect(register)
    else:
        return render(req, 'register.html')

    
def otp_confirmation(req):
    if req.method == 'POST':
        uname = req.POST.get('uname')
        user_otp = req.POST.get('otp')
        try:
            user = User.objects.get(username=uname)
            generated_otp = Otp.objects.get(user=user)
    
            if generated_otp.otp == user_otp:
                generated_otp.delete()
                return redirect(user_login)
            else:
                messages.warning(req, 'Invalid OTP')
                return redirect(otp_confirmation)
        except User.DoesNotExist:
            messages.warning(req, 'User does not exist')
            return redirect(otp_confirmation)
        except Otp.DoesNotExist:
            messages.warning(req, 'OTP not found or expired')
            return redirect(otp_confirmation)
    return render(req, 'otp.html')


def user_home(request):
    if 'admin' not in request.session:
        categories = Category.objects.all()  
        providers = ServiceProvider.objects.all()
        locations = ServiceProvider.objects.values_list('location', flat=True).distinct()
        print(locations)
        locations = sorted(set(loc.capitalize() for loc in locations if loc))
        return render(request, 'user/home.html', {'providers': providers, 'locations': locations, 'categories':categories})
    else: 
        return redirect(admin_home)
    

def category_providers(request, category_id):
    category = Category.objects.get(id=category_id)
    service_providers = ServiceProvider.objects.filter(category=category)
    return render(request, 'user/cat_prov.html', {'category': category, 'service_providers': service_providers})

def filter_by_location(request):
    location = request.GET.get('location', None)

    providers = ServiceProvider.objects.filter(location__iexact=location) if location else ServiceProvider.objects.all()

    locations = ServiceProvider.objects.values_list('location', flat=True).distinct()
    locations = sorted(set(loc.capitalize() for loc in locations if loc))

    return render(request, 'partials/provider_list.html', {
        'providers': providers,
        'locations': locations,  
    })


def search_providers(request):
    query = request.GET.get('query', '').strip()
    location = request.GET.get('location', '').strip()

    providers = ServiceProvider.objects.all()

    if query:
        providers = providers.filter(
            Q(name__icontains=query) |
            Q(category__category__icontains=query) |
            Q(location__icontains=query)
        )

    if location:
        providers = providers.filter(location__icontains=location)

    return render(request, 'partials/provider_list.html', {'providers': providers})

def addWishlist(req,pid):
    if 'user' in req.session:
        pro=ServiceProvider.objects.get(pk=pid)
        user=User.objects.get(username=req.session['user'])
        try:
            data=Wishlist.objects.get(user=user,pro=pro)
            if data:
                return redirect(viewWishlist)
        except:
            data=Wishlist.objects.create(user=user,pro=pro)
            data.save()
        return redirect(viewWishlist)
    else:
        return redirect(user_login)  

def viewWishlist(req):
    if 'user' in req.session:
        user=User.objects.get(username=req.session['user'])
        data=Wishlist.objects.filter(user=user)
        return render(req,'user/wishlist.html',{'data':data})
    else:
        return redirect(user_login) 

def deleteWishlist(req,pid):
    if 'user' in req.session:
        data=Wishlist.objects.get(pk=pid)
        data.delete()
        return redirect(viewWishlist)
    else:
        return redirect(user_login) 


# def view_details(request, id):
#     if 'user' in request.session:
#         provider = get_object_or_404(ServiceProvider, pk=id)
#         reviews = Review.objects.filter(provider=provider)

#         if request.method == "POST":
#             if 'date' in request.POST:
#                 date = request.POST.get("date")
#                 time = request.POST.get("time")
#                 phone = request.POST.get("phone")
#                 address = request.POST.get("address")

#                 if not phone or not address:
#                     messages.error(request, "Please fill all fields.")
#                     return redirect(view_details, id=id)

                
#                 existing_booking = Booking.objects.filter(
#                     provider=provider, date=date, time=time
#                 ).exists()

#                 if existing_booking:
#                     messages.error(request, "This time slot is already booked. Please choose another time.")
#                     return redirect(view_details, id=id)

#                 booking = Booking.objects.create(
#                     provider=provider,
#                     user=request.user,  
#                     date=date,
#                     time=time,
#                     phone=phone,
#                     address=address,
#                     status="Pending"
#                 )

#                 send_mail(
#                     subject="Booking Request Received",
#                     message=f"Dear {request.user.username},\n\n"
#                             f"Your booking request with {provider.name} has been received and is pending confirmation.\n\n"
#                             f"📅 Date: {booking.date}\n"
#                             f"⏰ Time: {booking.time}\n"
#                             f"📞 Phone: {booking.phone}\n"
#                             f"🏠 Address: {booking.address}\n\n"
#                             f"You will be notified once it is confirmed.\n\n"
#                             f"Thank you for using our service!\n\n"
#                             f"Best regards,\nYour Service Team",
#                     from_email=settings.EMAIL_HOST_USER,
#                     recipient_list=[request.user.email],
#                     fail_silently=False,
#                 )

                
#                 return redirect(user_bookings)

#             elif 'review' in request.POST:
#                 rating = request.POST.get("rating")
#                 message = request.POST.get("message")

#                 if not rating or int(rating) < 1 or int(rating) > 5:
#                     messages.error(request, "Invalid rating. Please select between 1-5 stars.")
#                     return redirect('view_details', id=id)

#                 Review.objects.create(
#                     provider=provider,
#                     user=request.user,  
#                     rating=int(rating),
#                     message=message
#                 )

#                 send_mail(
#                     subject="Thank You for Your Review!",
#                     message=f"Dear {request.user.username},\n\n"
#                             f"Thank you for leaving a review for {provider.name}.\n\n"
#                             f"🌟 Your Rating: {rating} / 5\n"
#                             f"💬 Your Review: \"{message}\"\n\n"
#                             f"We appreciate your feedback and hope to serve you again!\n\n"
#                             f"Best regards,\nYour Service Team",
#                     from_email=settings.EMAIL_HOST_USER,
#                     recipient_list=[request.user.email],
#                     fail_silently=False,
#                 )

#                 messages.success(request, "Review submitted successfully!")
#                 return redirect(view_details, id=id)

#         return render(request, 'user/view_details.html', {'provider': provider, 'reviews': reviews})

#     else:
#         return redirect(user_login)

def view_details(request, id):
    if 'user' in request.session:
        provider = get_object_or_404(ServiceProvider, pk=id)
        reviews = Review.objects.filter(provider=provider)

        # Fetch user's saved addresses (which include phone numbers)
        saved_addresses = Address.objects.filter(user=request.user)

        if request.method == "POST":
            # Handle Booking Submission
            if 'date' in request.POST:
                date = request.POST.get("date")
                time = request.POST.get("time")

                # Handle address selection (address & phone are together)
                selected_address_id = request.POST.get("selected_address")
                new_address_line = request.POST.get("new_address")
                new_phone_number = request.POST.get("new_phone")

                if selected_address_id:
                    address = Address.objects.get(id=selected_address_id)
                elif new_address_line and new_phone_number:
                    address = Address.objects.create(
                        user=request.user, 
                        address_line=new_address_line, 
                        phone_number=new_phone_number
                    )
                else:
                    messages.error(request, "Please provide or select an address and phone number.")
                    return redirect(view_details, id=id)

                # Check for existing booking
                existing_booking = Booking.objects.filter(
                    provider=provider, date=date, time=time
                ).exists()

                if existing_booking:
                    messages.error(request, "This time slot is already booked. Please choose another time.")
                    return redirect(view_details, id=id)

                # Create booking
                booking = Booking.objects.create(
                    provider=provider,
                    user=request.user,
                    date=date,
                    time=time,
                    phone=address.phone_number,
                    address=address.address_line,
                    status="Pending"
                )

                # Send booking confirmation email
                send_mail(
                    subject="Booking Request Received",
                    message=f"Dear {request.user.username},\n\n"
                            f"Your booking request with {provider.name} has been received and is pending confirmation.\n\n"
                            f"📅 Date: {booking.date}\n"
                            f"⏰ Time: {booking.time}\n"
                            f"📞 Phone: {booking.phone}\n"
                            f"🏠 Address: {booking.address}\n\n"
                            f"You will be notified once it is confirmed.\n\n"
                            f"Thank you for using our service!\n\n"
                            f"Best regards,\nYour Service Team",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                return redirect(user_bookings)

            # Handle Review Submission
            elif 'review' in request.POST:
                rating = request.POST.get("rating")
                message = request.POST.get("message")

                if not rating or int(rating) < 1 or int(rating) > 5:
                    messages.error(request, "Invalid rating. Please select between 1-5 stars.")
                    return redirect(view_details, id=id)

                # Create review
                Review.objects.create(
                    provider=provider,
                    user=request.user,
                    rating=int(rating),
                    message=message
                )

                # Send review thank-you email
                send_mail(
                    subject="Thank You for Your Review!",
                    message=f"Dear {request.user.username},\n\n"
                            f"Thank you for leaving a review for {provider.name}.\n\n"
                            f"🌟 Your Rating: {rating} / 5\n"
                            f"💬 Your Review: \"{message}\"\n\n"
                            f"We appreciate your feedback and hope to serve you again!\n\n"
                            f"Best regards,\nYour Service Team",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.success(request, "Review submitted successfully!")
                return redirect(view_details, id=id)

        return render(request, 'user/view_details.html', {
            'provider': provider,
            'reviews': reviews,
            'saved_addresses': saved_addresses
        })

    else:
        return redirect(user_login)

# def book_now(request, provider_id):
#     if 'user' in request.session:
#         provider = get_object_or_404(ServiceProvider, id=provider_id)

#         if request.method == "POST":
#             form = BookingForm(request.POST)
#             if form.is_valid():
#                 booking_date = form.cleaned_data['date']
#                 booking_time = form.cleaned_data['time']

               
#                 existing_booking = Booking.objects.filter(
#                     provider=provider, date=booking_date, time=booking_time
#                 ).exists()

#                 if existing_booking:
#                     messages.error(request, "This time slot is already booked. Please choose another time.")
#                     return redirect('book_now', provider_id=provider.id)

                
#                 booking = form.save(commit=False)
#                 booking.provider = provider
#                 booking.user = request.user  
#                 booking.status = "Pending"  
#                 booking.save()

               
#                 send_mail(
#                     subject="Booking Request Received",
#                     message=f"Dear {request.user.username},\n\n"
#                             f"Your booking request with {provider.name} has been received and is pending confirmation.\n\n"
#                             f"📅 Date: {booking.date}\n"
#                             f"⏰ Time: {booking.time}\n"
#                             f"📞 Phone: {booking.phone}\n"
#                             f"🏠 Address: {booking.address}\n\n"
#                             f"You will be notified once it is confirmed.\n\n"
#                             f"Thank you for using our service!\n\n"
#                             f"Best regards,\nYour Service Team",
#                     from_email=settings.EMAIL_HOST_USER,
#                     recipient_list=[request.user.email],
#                     fail_silently=False,
#                 )

            
#                 return redirect(user_bookings)  

#         else:
#             form = BookingForm()

#         return render(request, 'user/book_now.html', {'form': form, 'provider': provider})
#     else:
#         return redirect(user_login)

def cancel_booking(request, booking_id):
    if 'user' in request.session:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if booking.status == 'Pending':
            booking.status = 'Canceled'
            booking.delete()
            messages.success(request, "Your booking has been canceled successfully.")
        else:
            messages.warning(request, "You can only cancel pending bookings.")

        return redirect(user_bookings)
    else:
        return redirect(user_login)

def book_now(request, provider_id):
    if 'user' in request.session:
        provider = get_object_or_404(ServiceProvider, id=provider_id)

        if request.method == "POST":
            form = BookingForm(request.POST, user=request.user)
            if form.is_valid():
                booking_date = form.cleaned_data['date']
                booking_time = form.cleaned_data['time']
                selected_phone = form.cleaned_data.get('phone')
                new_phone = form.cleaned_data.get('new_phone')
                selected_address = form.cleaned_data.get('address')
                new_address = form.cleaned_data.get('new_address')

                existing_booking = Booking.objects.filter(
                    provider=provider, date=booking_date, time=booking_time
                ).exists()

                if existing_booking:
                    messages.error(request, "This time slot is already booked. Please choose another time.")
                    return redirect('book_now', provider_id=provider.id)

                booking = form.save(commit=False)
                booking.provider = provider
                booking.user = request.user
                booking.status = "Pending"

                # Handle new phone number or selected phone
                if new_phone:
                    booking.phone = new_phone
                else:
                    booking.phone = selected_phone

                # Handle new address or selected address
                if new_address:
                    # Save new address in the Address model
                    address_obj, created = Address.objects.get_or_create(
                        user=request.user,
                        address_line=new_address,
                        phone_number=booking.phone  # Use the selected or new phone
                    )
                    booking.address = new_address
                else:
                    address_obj = Address.objects.get(id=selected_address)
                    booking.address = address_obj.address_line

                booking.save()

                send_mail(
                    subject="Booking Request Received",
                    message=f"Dear {request.user.username},\n\n"
                            f"Your booking request with {provider.name} has been received and is pending confirmation.\n\n"
                            f"📅 Date: {booking.date}\n"
                            f"⏰ Time: {booking.time}\n"
                            f"📞 Phone: {booking.phone}\n"
                            f"🏠 Address: {booking.address}\n\n"
                            f"You will be notified once it is confirmed.\n\n"
                            f"Thank you for using our service!\n\n"
                            f"Best regards,\nYour Service Team",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                return redirect(user_bookings)

        else:
            form = BookingForm(user=request.user)

        return render(request, 'user/book_now.html', {'form': form, 'provider': provider})
    else:
        return redirect(user_login)

    
def user_bookings(req):
    if 'user' in req.session:
        bookings = Booking.objects.filter(user=req.user).order_by('-date')
        return render(req, 'user/user_bookings.html', {'bookings': bookings})
    else:
        return redirect(user_login)
    

def order_payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        if booking.payment_status == 'Paid':
            return render(request, 'error.html', {'message': 'Payment already completed.'})

       
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

       
        razorpay_order = client.order.create({
            "amount": int(booking.payment_amount * 100),  
            "currency": "INR",
            "payment_capture": "1",  
        })

        order_id = razorpay_order['id']

    
        return render(
            request,
            "user/payment.html",  
            {
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order_id": order_id,
                "booking_id": booking_id,
                "callback_url":"http://127.0.0.1:8000/razorpay/callback/",  
            },
        )

    except Booking.DoesNotExist:
        return render(request, {'message': 'Booking not found'})


@csrf_exempt
def callback(request):

    payment_id = request.POST.get("razorpay_payment_id")
    order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")

 
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

   
    params = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature,
    }

    try:
       
        client.utility.verify_payment_signature(params)
        booking = Booking.objects.get(id=request.POST['booking_id'])
        booking.payment_status = 'Paid'
        booking.advance_paid = True  
        booking.save()
        return redirect(user_bookings)

    except Exception as e:
        
        return JsonResponse({"status": "failure", "message": str(e)}, status=400)
