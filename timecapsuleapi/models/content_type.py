from django.db import models

class ContentType(models.Model):
    name = models.CharField(max_length=50)
    # Possible values: 'story', 'prediction', 'memory'