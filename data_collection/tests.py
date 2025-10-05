from unittest.mock import patch, MagicMock
from django.test import TestCase
from .models import RemoteServer, RemoteServerStatus
from datetime import timedelta
from . import tasks


class PollAllServersTaskTest(TestCase):
    """Тесты для задачи Celery - poll_all_servers"""

    def setUp(self):
        self.server = RemoteServer.objects.create(
            name="TestServer", url="http://example.com/api/status"
        )

    @patch("data_collection.tasks.requests.get")
    def test_poll_all_servers_success(self, mock_get):
        """Тест успешного опроса сервера и сохранения статуса"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "cpu": 42,
            "mem": "55%",
            "disk": "77%",
            "uptime": "1h 2m 3s",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        tasks.poll_all_servers()

        status = RemoteServerStatus.objects.get(server=self.server)
        self.assertEqual(status.cpu, 42)
        self.assertEqual(status.mem, 55)
        self.assertEqual(status.disk, 77)
        self.assertTrue(status.uptime.total_seconds() > 0)


class RemoteServerModelTest(TestCase):
    """Тесты для модели RemoteServer"""

    def test_create(self):
        """Тест создания модели RemoteServer"""
        server = RemoteServer.objects.create(
            name="TestServer", url="http://example.com"
        )
        self.assertEqual(server.url, "http://example.com")


class RemoteServerStatusModelTest(TestCase):
    """Тесты для модели RemoteServerStatus"""

    def setUp(self):
        self.server = RemoteServer.objects.create(
            name="TestServer", url="http://example.com"
        )

    def test_create(self):
        """Тест создания модели RemoteServerStatus"""
        status = RemoteServerStatus.objects.create(
            server=self.server,
            cpu=50,
            mem=60,
            disk=70,
            uptime=timedelta(hours=1, minutes=30),
        )
        self.assertEqual(status.cpu, 50)
        self.assertEqual(status.mem, 60)
        self.assertEqual(status.disk, 70)
        self.assertEqual(status.server, self.server)
