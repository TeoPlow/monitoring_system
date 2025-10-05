from django.db import models
from data_collection.models import RemoteServerStatus

class Incidents(models.Model):
    incident_type = models.CharField(max_length=100)
    incident_status = models.ForeignKey(RemoteServerStatus, on_delete=models.CASCADE)

    def __str__(self):
        return f"Incident {self.id} on {self.incident_status.server.name} - {self.incident_type}:{self.incident_status}"
