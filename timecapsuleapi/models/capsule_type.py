from django.db import models

class CapsuleType(models.Model):
    name = models.CharField(max_length=255)
