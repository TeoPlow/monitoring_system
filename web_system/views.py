import os
import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .middleware import token_store
from incident_monitoring.models import Incidents


@csrf_exempt
def login_view(request):
    """Вьюха для входа пользователя c cозданием токена"""

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        username = data.get("username")
        password = data.get("password")
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv(
            "ADMIN_PASSWORD"
        ):
            token = uuid.uuid4().hex
            token_store.add(token)
            response = JsonResponse({"success": True})
            response.set_cookie("auth_token", token, httponly=True)
            return response
        return JsonResponse(
            {"error": "Invalid password or username"}, status=401
        )


@csrf_exempt
def logout_view(request):
    """Вьюха для выхода пользователя с удалением токена"""

    token = request.COOKIES.get("auth_token")
    if token:
        token_store.remove(token)
    response = JsonResponse({"success": True})
    response.delete_cookie("auth_token")
    return response


def incidents_view(request):
    """Вьюха для получения списка инцидентов"""

    incidents = Incidents.objects.select_related("incident_status__server")
    result = []
    for incident in incidents:
        status = incident.incident_status
        result.append(
            {
                "incident_type": incident.incident_type,
                "server_name": status.server.name,
                "cpu": status.cpu,
                "mem": status.mem,
                "disk": status.disk,
                "uptime": str(status.uptime),
                "checked_at": status.checked_at.isoformat(),
            }
        )
    return JsonResponse({"incidents": result})


def incidents_page(request):
    """Вьюха для рендера страницы инцидентов"""

    return render(request, "web_system/incidents.html")
