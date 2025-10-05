from django.urls import path
from . import views


urlpatterns = [
    path("api/login/", views.login_view, name="login"),
    path("api/logout/", views.logout_view, name="logout"),
    path("api/incidents/", views.incidents_view, name="incidents"),
    path("incidents/", views.incidents_page, name="incidents_page"),
]
