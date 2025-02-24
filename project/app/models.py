from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    category = models.TextField()
    img = models.FileField()


class ServiceProvider(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    profile = models.FileField()
    name = models.TextField()
    phone = models.IntegerField(unique=True)
    experience = models.IntegerField()
    availability = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    location = models.TextField()
    des = models.TextField()
    charge = models.FloatField()
    working_hours = models.TextField()