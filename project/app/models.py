from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus

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
    
    def update_rating(self):
        """Update provider rating based on all reviews."""
        reviews = self.reviews.all() 
        total_reviews = reviews.count()
        if total_reviews > 0:
            avg_rating = sum(review.rating for review in reviews) / total_reviews
            self.rating = round(avg_rating, 1) 
        else:
            self.rating = 0  
        
        self.save()
    
class Otp(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.TextField()
    
    
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    pro=models.ForeignKey(ServiceProvider,on_delete=models.CASCADE)


class Review(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    rating = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.provider.update_rating()
    

        


class Booking(models.Model):
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)  
    address = models.TextField()  
    date = models.DateField()
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="Pending") 
    

    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')  
    advance_paid = models.BooleanField(default=False)  
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)  
    
    class Meta:
        unique_together = ('provider', 'date', 'time')

    def __str__(self):
        return f"Booking by {self.user.username} for {self.provider.name}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line = models.TextField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.address_line} ({self.phone_number})"