from django.db import models

class Prediction(models.Model):
    capsule_content = models.ForeignKey("TimeCapsuleContent", on_delete=models.CASCADE, related_name="predictions")
    prediction_text = models.TextField()
    category = models.CharField(max_length=50, null=True, blank=True)
    verification_status = models.ForeignKey("VerificationStatus", on_delete=models.CASCADE, related_name="predictions")
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_user = models.ForeignKey("UserProfile", on_delete=models.SET_NULL, related_name="verified_predictions", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)