from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    def __str__(self):
        return self.username
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TRADER', 'Trader'),
        ('SALES_REP', 'Sales Representative'),
        ('CUSTOMER', 'Customer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
