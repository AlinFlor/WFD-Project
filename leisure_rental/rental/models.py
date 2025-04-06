from django.db import models
from django.contrib.authmodels import AbstractUser

USER_ROLES = (
    ('CUSTOMER', 'Customer'),
    ('ADMIN', 'Admin'),
)

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=USER_ROLES, default='CUSTOMER')
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    daily_rate = models.DecimalField(max_digits=6, decimal_places=2)