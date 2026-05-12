from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20)
    id_type = models.CharField(max_length=10)

    def __str__(self):
        return self.user.email
