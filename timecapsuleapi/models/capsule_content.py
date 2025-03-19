from django.db import models

class TimeCapsuleContent(models.Model):
    capsule = models.ForeignKey("TimeCapsule", on_delete=models.CASCADE, related_name="contents")
    content_type = models.ForeignKey("ContentType", on_delete=models.CASCADE, related_name="contents")
    content = models.TextField()
    media_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)