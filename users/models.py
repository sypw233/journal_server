from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, '普通用户'),
        (2, 'root用户'),
    )
    
    email = models.EmailField(unique=True,blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    last_data_sync_time = models.DateTimeField(auto_now=True)
    register_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username


