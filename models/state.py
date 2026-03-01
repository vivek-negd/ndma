from django.db import models


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lgd_code = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)

    class Meta:
        db_table = "models_state"

    def __str__(self):
        return self.name