import requests
from celery import shared_task
from .models import RemoteServer, RemoteServerStatus
from pytimeparse.timeparse import timeparse
from datetime import timedelta

def parse_uptime(uptime_str):
    seconds = timeparse(uptime_str)
    if seconds is not None:
        return timedelta(seconds=seconds)
    else:
        # TODO: Логировать ошибку парсинга
        return timedelta(0)

def parse_percent(val):
    """Преобразует строку вида '43%' в int 43"""
    try:
        return int(str(val).replace('%', ''))
    except ValueError:
        # TODO: Логировать ошибку парсинга
        return 0

@shared_task
def poll_all_servers():
    for server in RemoteServer.objects.all():
        try:
            response = requests.get(server.url, timeout=10)
            response.raise_for_status()
            data = response.json()

            RemoteServerStatus.objects.create(
                server=server,
                cpu=int(data.get('cpu', 0)),
                mem=parse_percent(data.get('mem', 0)),
                disk=parse_percent(data.get('disk', 0)),
                uptime=parse_uptime(data.get('uptime', '0s')),
            )
        except Exception as e:
            # TODO: Добавить логирование ошибок
            pass
