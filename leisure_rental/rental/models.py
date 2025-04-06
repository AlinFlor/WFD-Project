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
    available = models. BooleanField(default=True)
    condition = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='Reserved')
    
