from django.db import models
from .state import State

class District(models.Model):
    name = models.CharField(max_length=100)
    lgd_code = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="districts"
    )
    volunteer_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "models_district"
        unique_together = ("name", "state")

    def __str__(self):
        return f"{self.name} - {self.state.name}"