from django.db import models

class RemoteServer(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.name

class RemoteServerStatus(models.Model):
    server = models.ForeignKey(RemoteServer, on_delete=models.CASCADE, related_name='statuses')
    cpu = models.IntegerField(help_text="CPU usage in percent")
    mem = models.IntegerField(help_text="Memory usage in percent")
    disk = models.IntegerField(help_text="Disk usage in percent")
    uptime = models.DurationField(help_text="Uptime")
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name} - {self.checked_at}"
