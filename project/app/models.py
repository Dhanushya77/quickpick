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
    
    def update_rating(self):
        """Update provider rating based on all reviews."""
        reviews = self.reviews.all()  # Get all reviews for this provider
        total_reviews = reviews.count()
        if total_reviews > 0:
            avg_rating = sum(review.rating for review in reviews) / total_reviews
            self.rating = round(avg_rating, 1)  # Round to 1 decimal place
        else:
            self.rating = 0  # Reset to 0 if no reviews exist
        
        self.save()
    
class Otp(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.TextField()
    
    
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    pro=models.ForeignKey(ServiceProvider,on_delete=models.CASCADE)




class Review(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # To track which user submitted the review
    rating = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.provider.update_rating()
    

            



class Booking(models.Model):
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)  # Store user phone number
    address = models.TextField()  # Store user address
    date = models.DateField()
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="Pending")  # Booking status

    def __str__(self):
        return f"Booking by {self.user.username} for {self.provider.name}"
