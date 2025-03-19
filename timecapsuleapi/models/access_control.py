from django.db import models

class AccessControl(models.Model):
    capsule = models.ForeignKey("TimeCapsule", on_delete=models.CASCADE, related_name="access_controls")
    user = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="capsule_permissions")
    permission_level = models.ForeignKey("PermissionLevel", on_delete=models.CASCADE, related_name="access_controls")
    expires_at = models.DateTimeField(null=True, blank=True)