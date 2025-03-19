from django.db import models

class PermissionLevel(models.Model):
    name = models.CharField(max_length=50)
    # Possible values: 'owner', 'viewer', 'contributor'