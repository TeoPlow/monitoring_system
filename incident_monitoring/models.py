from django.db import models
from data_collection.models import RemoteServerStatus


class Incidents(models.Model):
    """Модель для хранения инцидентов"""

    incident_type = models.CharField(max_length=100)
    incident_status = models.ForeignKey(
        RemoteServerStatus, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Incident {self.id} - {self.incident_type}"
