from django.test import TestCase
from data_collection.models import RemoteServer, RemoteServerStatus
from incident_monitoring.tasks import check_cpu_incidents
from .models import Incidents
from django.utils import timezone
from datetime import timedelta


class IncidentsModelTest(TestCase):
    """Тесты для модели Incidents"""

    def setUp(self):
        self.server = RemoteServer.objects.create(
            name="test_server", url="http://localhost"
        )
        self.status_cpu = RemoteServerStatus.objects.create(
            server=self.server,
            cpu=90,
            mem=80,
            disk=70,
            uptime=timedelta(hours=1),
            checked_at=timezone.now(),
        )

    def test_create_incident(self):
        """Тест создания модели Incidents"""

        incident = Incidents.objects.create(
            incident_type="High CPU Usage", incident_status=self.status_cpu
        )
        self.assertEqual(incident.incident_type, "High CPU Usage")
        self.assertEqual(incident.incident_status, self.status_cpu)


class CeleryTasksTest(TestCase):
    """Тесты для задач Celery"""

    def setUp(self):
        self.server = RemoteServer.objects.create(
            name="TestServer", url="http://localhost"
        )
        now = timezone.now()
        self.status_cpu = RemoteServerStatus.objects.create(
            server=self.server,
            cpu=99,
            mem=50,
            disk=50,
            uptime=timedelta(hours=1),
            checked_at=now,
        )

    def test_check_cpu_incidents(self):
        """Тест задачи поиска CPU инцидентов"""

        self.assertEqual(Incidents.objects.count(), 0)
        check_cpu_incidents()
        self.assertEqual(Incidents.objects.count(), 1)
        incident = Incidents.objects.first()
        self.assertEqual(incident.incident_type, "High CPU Usage")
        self.assertEqual(incident.incident_status, self.status_cpu)
        check_cpu_incidents()
        self.assertEqual(Incidents.objects.count(), 1)
