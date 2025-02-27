from django.urls import path
from . import views

urlpatterns = [
    path('',views.dummy_home),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('register',views.register),
    # ---------------admin----------------
    path('admin_home',views.admin_home),
    path('category',views.category),
    path('view_category',views.view_category),
    path('delete_category/<id>',views.delete_category),
    path('add_pro',views.add_pro),
    path('edit_pro/<pid>',views.edit_pro),
    path('delete_pro/<pid>',views.delete_pro),
    
]