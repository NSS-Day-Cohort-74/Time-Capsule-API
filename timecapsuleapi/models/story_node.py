from django.db import models

class StoryNode(models.Model):
    capsule_content = models.ForeignKey("TimeCapsuleContent", on_delete=models.CASCADE, related_name="story_nodes")
    parent_node = models.ForeignKey("self", on_delete=models.CASCADE, related_name="child_nodes", null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)