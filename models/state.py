from django.db import models
from django.utils import timezone


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lgd_code = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    volunteer_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "models_state"

    def __str__(self):
        return self.name