from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(ServiceProvider)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Booking)