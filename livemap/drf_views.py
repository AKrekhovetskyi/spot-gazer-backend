from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, ClassVar

from django.db.models import Q, QuerySet
from rest_framework import permissions, viewsets
from rest_framework.serializers import ValidationError

from .models import Occupancy, VideoStreamSource
from .serializers import OccupancySerializer, VideoStreamSourceSerializer


class VideoStreamSourceViewSet(viewsets.ModelViewSet):
    queryset = VideoStreamSource.objects.all().select_related(
        "parking_lot__address", "parking_lot__address__city", "parking_lot__address__city__country"
    )
    serializer_class = VideoStreamSourceSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[VideoStreamSource, VideoStreamSource]:  # pyright: ignore[reportIncompatibleMethodOverride]
        queryset = self.queryset
        active_only = self.request.query_params.get("active_only")  # pyright: ignore[reportAttributeAccessIssue]
        if active_only:
            queryset = queryset.filter(is_active=True)

        mark_in_use_until = self.request.query_params.get("mark_in_use_until")  # pyright: ignore[reportAttributeAccessIssue]
        if mark_in_use_until and self.request.user.is_authenticated:
            # 0) Validate the incoming ISO-8601 string.
            try:
                in_use_until = datetime.fromisoformat(mark_in_use_until)
            except ValueError as error:
                raise ValidationError({"mark_in_use_until": "Must be a valid ISO 8601 datetime string"}) from error

            now = datetime.now(UTC)

            # 1) Find all the items whose `in_use_until` field is either `null` or has an expired date and time.
            not_in_use_q = Q(in_use_until__isnull=True) | Q(in_use_until__lt=now)
            candidates = queryset.filter(not_in_use_q)

            # 2) Capture their PKs (so we know exactly which ones).
            ids_to_update = list(candidates.values_list("pk", flat=True))

            # 3) Bulk-update just those rows.
            queryset.filter(pk__in=ids_to_update).update(in_use_until=in_use_until)

            # 4) Return those exact rows (now updated).
            return queryset.filter(pk__in=ids_to_update)

        return queryset

    def list(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        # There may be several CCTV cameras in one parking lot.
        # The code below groups parking lots by video streams.
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        video_streams = serializer.data
        stream_details = defaultdict(list)

        for stream in video_streams:
            stream_details[stream["parking_lot_id"]].append(
                {
                    "id": stream["id"],
                    "stream_source": stream["stream_source"],
                    "is_active": stream["is_active"],
                    "in_use_until": stream.get("in_use_until"),
                }
            )

        grouped_video_streams = []
        for video_stream in video_streams:
            try:
                grouped_video_streams.append(
                    {
                        "parking_lot_address": video_stream["parking_lot_address"],
                        "parking_lot_id": video_stream["parking_lot_id"],
                        "processing_rate": video_stream["processing_rate"],
                        "streams": stream_details.pop(video_stream["parking_lot_id"]),
                    }
                )
            except KeyError:
                # The `KeyError` is expected because there are might be duplicates in the `video_streams`.
                continue

        return self.get_paginated_response(grouped_video_streams)


class OccupancyViewSet(viewsets.ModelViewSet):
    queryset = Occupancy.objects.all().select_related(
        "parking_lot__address", "parking_lot__address__city", "parking_lot__address__city__country"
    )
    serializer_class = OccupancySerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]
