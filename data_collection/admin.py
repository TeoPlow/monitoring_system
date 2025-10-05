
from django.contrib import admin
from .models import RemoteServer

@admin.register(RemoteServer)
class RemoteServerAdmin(admin.ModelAdmin):
	list_display = ("name", "url")
	search_fields = ("name", "url")
