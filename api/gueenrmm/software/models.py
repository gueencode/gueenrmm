from django.db import models

from gueenrmm.models import PermissionQuerySet
from agents.models import Agent


class ChocoSoftware(models.Model):
    chocos = models.JSONField()
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{len(self.chocos)} - {self.added}"


class InstalledSoftware(models.Model):
    objects = PermissionQuerySet.as_manager()

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    software = models.JSONField()

    def __str__(self):
        return self.agent.hostname
