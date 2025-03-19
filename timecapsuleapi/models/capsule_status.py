from django.db import models

class CapsuleStatus(models.Model):
    name = models.CharField(max_length=255)

