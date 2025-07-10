from django.urls import include, path
from rest_framework import routers

from livemap.drf_views import VideoStreamSourceViewSet
from livemap.views import index

router = routers.DefaultRouter()
router.register(r"video-stream-sources", VideoStreamSourceViewSet)

urlpatterns = [
    path("livemap/", index, name="index"),
    path("api/", include(router.urls)),
]

app_name = "livemap"
