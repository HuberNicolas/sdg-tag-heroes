from django.db import models

from .user import CustomUser


# Model for the Labeler role, extends CustomUser
class Labeler(CustomUser):
    labeling_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Labeler"
        verbose_name_plural = "Labelers"
