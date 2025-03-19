from django.db import models

class VerificationStatus(models.Model):
    name = models.CharField(max_length=50)
    # Possible values: 'pending', 'verified', 'disproved'