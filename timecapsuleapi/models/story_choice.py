from django.db import models

class StoryChoice(models.Model):
    node = models.ForeignKey("StoryNode", on_delete=models.CASCADE, related_name="choices")
    choice_text = models.TextField()
    next_node = models.ForeignKey("StoryNode", on_delete=models.CASCADE, related_name="incoming_choices")
    created_at = models.DateTimeField(auto_now_add=True)