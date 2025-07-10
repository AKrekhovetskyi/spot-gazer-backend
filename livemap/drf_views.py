from typing import ClassVar

from django.db.models import QuerySet
from rest_framework import permissions, viewsets

from .models import VideoStreamSource
from .serializers import VideoStreamSourceSerializer


class VideoStreamSourceViewSet(viewsets.ModelViewSet):
    queryset = VideoStreamSource.objects.all().select_related(
        "parking_lot__address", "parking_lot__address__city", "parking_lot__address__city__country"
    )
    serializer_class = VideoStreamSourceSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[VideoStreamSource, VideoStreamSource]:  # pyright: ignore[reportIncompatibleMethodOverride]
        active_only = self.request.query_params.get("active_only")  # pyright: ignore[reportAttributeAccessIssue]
        if active_only:
            return self.queryset.filter(is_active=True)
        return self.queryset
