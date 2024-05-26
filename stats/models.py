from django.db import models


class Stats(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    show = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
