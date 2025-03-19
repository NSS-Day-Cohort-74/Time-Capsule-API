from django.db import models

class DiscussionThread(models.Model):
    capsule = models.ForeignKey("TimeCapsule", on_delete=models.CASCADE, related_name="discussion_threads")
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="discussion_threads")
    created_at = models.DateTimeField(auto_now_add=True)