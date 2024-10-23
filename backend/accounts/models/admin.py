from django.db import models

from .user import CustomUser


# Model for the Admin role, extends CustomUser
class Admin(CustomUser):
    # Additional fields for Admin role can be added here if needed
    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
