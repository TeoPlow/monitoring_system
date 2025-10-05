import logging
import os
from datetime import timedelta, datetime
from pytimeparse.timeparse import timeparse
from celery import shared_task
from .models import Incidents
from data_collection.models import RemoteServer


log = logging.getLogger(__name__)

def check_incidents(incident_type, incidents, active_time):
    log.debug(f"Проверка инцидентов типа: {incident_type}")
    for incident in incidents:
        active_exists = Incidents.objects.filter(
            incident_type=incident_type,
            incident_status__server=incident.server,
            incident_status__checked_at__gte=incident.checked_at - timedelta(seconds=active_time),
        ).exists()
        log.debug(f"Инцидент {incident.id} уже активенен: {active_exists}")
        if not active_exists:
            log.debug(f"Добавление инцидента {incident.id} в БД")
            Incidents.objects.create(
                incident_type=incident_type,
                incident_status=incident
            )

@shared_task
def check_cpu_incidents():
    log.info("Запуск задачи поиска CPU инцидентов в БД")
    try:
        incident_type = "High CPU Usage"
        active_time = timeparse(os.getenv("INCIDENT_ACTIVE_TIME_CPU", "1h"))
        threshold_percent = int(os.getenv("CPU_USAGE_THRESHOLD", "85"))
        threeshold_time = timeparse(os.getenv("CPU_USAGE_TIME_THRESHOLD", "0m"))

        servers = RemoteServer.objects.all()

        problem_statuses = []
        for server in servers:
            statuses = server.statuses.filter(
                checked_at__gte=datetime.now() - timedelta(seconds=threeshold_time)
            )
            if statuses.exists() and not statuses.filter(cpu__lte=threshold_percent).exists():
                problem_statuses.extend(list(statuses))

        check_incidents(incident_type, problem_statuses, active_time)

    except Exception as e:
        log.error(f"Ошибка при поиске CPU инцидентов: {e}")
    else:
        log.info("Задача поиска CPU инцидентов завершена")

@shared_task
def check_memory_incidents():
    log.info("Запуск задачи поиска инцидентов c памятью в БД")
    try:
        incident_type = "High Memory Usage"
        active_time = timeparse(os.getenv("INCIDENT_ACTIVE_TIME_MEMORY", "1h"))
        threshold_percent = int(os.getenv("MEMORY_USAGE_THRESHOLD", "90"))
        threeshold_time = timeparse(os.getenv("MEMORY_USAGE_TIME_THRESHOLD", "30m"))

        servers = RemoteServer.objects.all()

        problem_statuses = []
        for server in servers:
            statuses = server.statuses.filter(
                checked_at__gte=datetime.now() - timedelta(seconds=threeshold_time)
            )
            if statuses.exists() and not statuses.filter(mem__lte=threshold_percent).exists():
                problem_statuses.extend(list(statuses))

        check_incidents(incident_type, problem_statuses, active_time)

    except Exception as e:
        log.error(f"Ошибка при поиске инцидентов с памятью: {e}")
    else:
        log.info("Задача поиска инцидентов с памятью завершена")

@shared_task
def check_disk_incidents():
    log.info("Запуск задачи поиска инцидентов с диском в БД")
    try:
        incident_type = "High Disk Usage"
        active_time = timeparse(os.getenv("INCIDENT_ACTIVE_TIME_DISK", "1h"))
        threshold_percent = int(os.getenv("DISK_USAGE_THRESHOLD", "95"))
        threeshold_time = timeparse(os.getenv("DISK_USAGE_TIME_THRESHOLD", "2h"))

        servers = RemoteServer.objects.all()

        problem_statuses = []
        for server in servers:
            statuses = server.statuses.filter(
                checked_at__gte=datetime.now() - timedelta(seconds=threeshold_time)
            )
            if statuses.exists() and not statuses.filter(disk__lte=threshold_percent).exists():
                problem_statuses.extend(list(statuses))

        check_incidents(incident_type, problem_statuses, active_time)

    except Exception as e:
        log.error(f"Ошибка при поиске инцидентов с диском: {e}")
    else:
        log.info("Задача поиска инцидентов с диском завершена")
