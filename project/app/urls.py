from django.urls import path
from . import views

urlpatterns = [
    path('',views.dummy_home),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('shop_home',views.shop_home),
]