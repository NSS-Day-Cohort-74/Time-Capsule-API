from django.db import models

class TimeCapsule(models.Model):
    creator = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="timecapsules")
    status = models.ForeignKey("CapsuleStatus", on_delete=models.CASCADE, related_name="timecapsules")
    type = models.ForeignKey("CapsuleType", on_delete=models.CASCADE, related_name="timecapsules")
    title = models.CharField(max_length=255)
    descriptions = models.TextField()
    opening_date = models.DateTimeField()
    location_x = models.FloatField()
    location_y = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

