from django.urls import path
from . import views

urlpatterns = [
    path('',views.dummy_home),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('admin_home',views.admin_home),
    path('category',views.category),
    path('view_category',views.view_category),
    path('delete_category/<id>',views.delete_category),

]