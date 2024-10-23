from django.db import models

from .labeler import Labeler


# Model for the Expert role, extends Labeler
class Expert(Labeler):
    expert_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Expert"
        verbose_name_plural = "Experts"
