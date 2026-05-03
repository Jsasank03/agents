# models.py
from django.db import models

class ParliamentSession(models.Model):
    title = models.CharField(max_length=200)
    speaker = models.CharField(max_length=100)
    duration = models.IntegerField()