from typing import ClassVar

from rest_framework import permissions, viewsets

from .models import VideoStreamSource
from .serializers import VideoStreamSourceSerializer


class VideoStreamSourceViewSet(viewsets.ModelViewSet):
    queryset = VideoStreamSource.objects.all().select_related(
        "parking_lot__address", "parking_lot__address__city", "parking_lot__address__city__country"
    )
    serializer_class = VideoStreamSourceSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]
