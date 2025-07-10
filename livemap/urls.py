from django.urls import include, path
from rest_framework import routers

from livemap.views import index

router = routers.DefaultRouter()
urlpatterns = [
    path("", index, name="index"),
    path("api/", include(router.urls)),
]

app_name = "livemap"
