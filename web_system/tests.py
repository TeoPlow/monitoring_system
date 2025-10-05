import os
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from .middleware import token_store, CustomAuthMiddleware
from django.urls import reverse
from . import views


class IncidentsViewTest(TestCase):
    """Тесты инцидентов"""

    def setUp(self):
        self.factory = RequestFactory()

    @patch("web_system.views.Incidents")
    def test_incidents_view_returns_data(self, mock_incidents):
        """Тест проверки возврата данных инцидентов с моками"""

        mock_status = MagicMock()
        mock_status.server.name = "Server1"
        mock_status.cpu = 10
        mock_status.mem = 20
        mock_status.disk = 30
        mock_status.uptime = "1:00:00"
        mock_status.checked_at.isoformat.return_value = "2025-10-05T12:00:00"

        mock_incident = MagicMock()
        mock_incident.incident_type = "CPU"
        mock_incident.incident_status = mock_status
        mock_incidents.objects.select_related.return_value = [mock_incident]

        request = self.factory.get("/web_system/api/incidents/")
        response = views.incidents_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("incidents", data)
        self.assertEqual(len(data["incidents"]), 1)
        self.assertEqual(data["incidents"][0]["server_name"], "Server1")

    def test_incidents_page_renders(self):
        """Тест проверки рендеринга страницы"""

        request = self.factory.get("/web_system/incidents/")
        response = views.incidents_page(request)
        self.assertEqual(response.status_code, 200)


class LoginLogoutViewTest(TestCase):
    """Тесты входа и выхода"""

    def setUp(self):
        self.factory = RequestFactory()
        self.username = "admin"
        self.password = "password"

    @patch.dict(
        os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"}
    )
    def test_login_success(self):
        """Тест успешного входа"""

        data = json.dumps(
            {"username": self.username, "password": self.password}
        )
        request = self.factory.post(
            reverse("login"), data, content_type="application/json"
        )
        response = views.login_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.cookies)
        self.assertJSONEqual(response.content, {"success": True})

    @patch.dict(
        os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"}
    )
    def test_login_invalid_credentials(self):
        """Тест входа с неправильным паролем"""

        data = json.dumps({"username": "test_bad", "password": "test_bad"})
        request = self.factory.post(
            reverse("login"), data, content_type="application/json"
        )
        response = views.login_view(request)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content, {"error": "Invalid credentials"}
        )

    def test_logout_removes_token_and_cookie(self):
        """Тест выхода и удаления токена"""

        request = self.factory.post(reverse("logout"))
        request.COOKIES["auth_token"] = "test_token123"
        response = views.logout_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})
        self.assertIn("auth_token", response.cookies)
        self.assertEqual(response.cookies["auth_token"]["max-age"], 0)


class TokenTest(TestCase):
    """Тесты для токенов"""

    def test_add_and_validate_token(self):
        """Тест добавления и проверки токена"""
        token = "test_token123"
        token_store.add(token)
        self.assertTrue(token_store.is_valid(token))
        token_store.remove(token)
        self.assertFalse(token_store.is_valid(token))


class CustomAuthMiddlewareTest(TestCase):
    """Тесты для самописного middleware аутентификации"""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CustomAuthMiddleware(lambda req: HttpResponse("ok"))
        self.token = "test_token123"
        token_store.add(self.token)

    def tearDown(self):
        token_store.remove(self.token)

    def test_allows_valid_token(self):
        """Тест на валидный токен"""

        request = self.factory.get("/web_system/api/incidents/")
        request.COOKIES["auth_token"] = self.token
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_blocks_invalid_token(self):
        """Тест на невалидный токен"""

        request = self.factory.get("/web_system/api/incidents/")
        request.COOKIES["auth_token"] = "badtoken"
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)

    def test_blocks_missing_token(self):
        """Тест на отсутствие токена"""

        request = self.factory.get("/web_system/api/incidents/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)
