from django.urls import include, path
from rest_framework import routers

from livemap.drf.views import OccupancyViewSet, VideoStreamSourceViewSet
from livemap.views import index

router = routers.DefaultRouter()
router.register(r"video-stream-sources", VideoStreamSourceViewSet)
router.register(r"occupancy", OccupancyViewSet)

urlpatterns = [
    path("livemap/", index, name="index"),
    path("api/", include(router.urls)),
]

app_name = "livemap"
