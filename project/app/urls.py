from django.urls import path
from . import views

urlpatterns = [
    # path('',views.dummy_home),
    path('login',views.user_login),
    path('logout',views.user_logout,name='logout'),
    path('register',views.register),
    path('otp',views.otp_confirmation),
    path('quick_logout',views.quick_logout),



    # ---------------admin----------------
    path('admin_home',views.admin_home),
    path('category',views.category),
    path('view_category',views.view_category),
    path('delete_category/<id>',views.delete_category),
    path('add_pro',views.add_pro),
    path('edit_pro/<pid>',views.edit_pro),
    path('delete_pro/<pid>',views.delete_pro),
    path('view_service/<cid>/', views.view_service),
    path('admin_bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin_confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('admin_decline-booking/<int:booking_id>/', views.decline_booking, name='decline_booking'),

    
    # ----------------user--------------------
    path('',views.user_home,name='user_home'),
    path('filter_by_location/', views.filter_by_location, name='filter_by_location'),
    path('search_providers/', views.search_providers, name='search_providers'),
    path('view_details/<id>',views.view_details),
    path('addWishlist/<pid>',views.addWishlist),
    path('viewWishlist',views.viewWishlist),
    path('deleteWishlist/<pid>',views.deleteWishlist),
    path('book-now/<int:provider_id>/', views.book_now, name='book_now'),
    path('user_bookings',views.user_bookings),
    path('order_payment/<booking_id>', views.order_payment, name='order_payment'),
    path('razorpay/callback/',views.callback,name="callback"),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('category/<int:category_id>/', views.category_providers, name='category_providers'), 
]