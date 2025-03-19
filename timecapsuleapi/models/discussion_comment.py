from django.db import models

class DiscussionComment(models.Model):
    thread = models.ForeignKey("DiscussionThread", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    author = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="discussion_comments")
    created_at = models.DateTimeField(auto_now_add=True)