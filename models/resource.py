from django.db import models


class Resource(models.Model):

    name = models.CharField(max_length=100)

    state_code = models.CharField(max_length=10)
    district_code = models.CharField(max_length=10)
    block_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name