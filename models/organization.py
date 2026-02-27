from django.db import models

# class Organization(models.Model):
#     organization_name = models.CharField(max_length=50, unique=True)
#     volunteer_count = models.PositiveIntegerField(default=0)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "models_organization"

#     def __str__(self):
#         return self.organization_name/

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "models_organization"

    def __str__(self):
        return self.name