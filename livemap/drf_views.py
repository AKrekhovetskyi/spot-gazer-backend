from typing import Any, ClassVar

from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.response import Response

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

    def list(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        # There may be several CCTV cameras in one parking lot.
        # The code below groups parking lots by video streams.
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        video_streams = serializer.data
        stream_details = {}
        for stream in video_streams:
            if stream["parking_lot_id"] in stream_details:
                stream_details[stream["parking_lot_id"]].append(
                    {"id": stream["id"], "stream_source": stream["stream_source"], "is_active": stream["is_active"]}
                )
            else:
                stream_details[stream["parking_lot_id"]] = [
                    {
                        "id": stream["id"],
                        "stream_source": stream["stream_source"],
                        "is_active": stream["is_active"],
                    }
                ]

        grouped_video_streams = []
        for video_stream in video_streams:
            try:
                grouped_video_streams.append(
                    {
                        "parking_lot": video_stream["parking_lot"],
                        "parking_lot_id": video_stream["parking_lot_id"],
                        "processing_rate": video_stream["processing_rate"],
                        "streams": stream_details.pop(video_stream["parking_lot_id"]),
                    }
                )
            except KeyError:
                # The `KeyError` is expected because there are might be duplicates in the `video_streams`.
                continue

        return Response(grouped_video_streams)
