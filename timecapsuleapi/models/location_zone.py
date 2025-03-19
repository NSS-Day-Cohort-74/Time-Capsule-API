from django.db import models

class LocationZone(models.Model):
    name = models.CharField(max_length=255)
    # For the boundary polygon, we'll use separate fields for simplicity
    # In a real-world scenario, you might want to use GeoDjango for proper spatial data
    boundary_data = models.JSONField()  # Store polygon coordinates as JSON
    restrictions = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)