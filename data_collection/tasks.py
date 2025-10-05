import logging
import requests
from celery import shared_task
from .models import RemoteServer, RemoteServerStatus
from pytimeparse.timeparse import timeparse
from datetime import timedelta

log = logging.getLogger(__name__)

def parse_uptime(uptime_str):
    seconds = timeparse(uptime_str)
    if seconds is not None:
        return timedelta(seconds=seconds)
    else:
        log.error(f"Ошибка парсинга: '{uptime_str}'")
        return timedelta(0)

def parse_percent(val):
    try:
        return int(str(val).replace('%', ''))
    except ValueError:
        log.error(f"Ошибка парсинга: '{val}'")
        return 0

@shared_task
def poll_all_servers():
    log.info("Запуск задачи опроса всех серверов")
    for server in RemoteServer.objects.all():
        try:
            log.info(f"Опрос сервера: {server.name} ({server.url})")
            response = requests.get(server.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            log.debug(f"Получил: {data})")

            RemoteServerStatus.objects.create(
                server=server,
                cpu=int(data.get('cpu', 0)),
                mem=parse_percent(data.get('mem', 0)),
                disk=parse_percent(data.get('disk', 0)),
                uptime=parse_uptime(data.get('uptime', '0s')),
            )
        except Exception as e:
            log.error(f"Ошибка при опросе сервера {server.name} ({server.url}): {e}")
        else:
            log.info(f"Данные успешно сохранены для сервера: {server.name}")
