from typing import Any

from rest_framework import serializers

from .models import Occupancy, ParkingLot, VideoStreamSource


def validate_parking_lot_id(parking_lot_id: int | None) -> int | None:
    if parking_lot_id and not ParkingLot.objects.filter(id=parking_lot_id).first():
        raise serializers.ValidationError(f"No parking lot found for the provided ID {parking_lot_id}")
    return parking_lot_id


class VideoStreamSourceSerializer(serializers.ModelSerializer):
    parking_lot_address = serializers.CharField(source="parking_lot.address", read_only=True)
    parking_lot_id = serializers.IntegerField(
        validators=[validate_parking_lot_id], help_text="ID of an existing parking lot."
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = VideoStreamSource
        fields = ("id", "parking_lot_address", "parking_lot_id", "stream_source", "processing_rate", "is_active")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        parking_lot_id = attrs.get("parking_lot_id")
        processing_rate = attrs.get("processing_rate")
        if processing_rate and not parking_lot_id:
            raise serializers.ValidationError(
                {
                    "parking_lot_id": "`parking_lot_id` field must be provided along with the `processing_rate` one",
                }
            )
        if parking_lot_id and processing_rate:
            video_stream = VideoStreamSource.objects.filter(parking_lot=parking_lot_id).first()
            if video_stream and video_stream.processing_rate != processing_rate:
                raise serializers.ValidationError(
                    {
                        "processing_rate": f"The processing rate for the parking lot {parking_lot_id} "
                        f"must be {video_stream.processing_rate} seconds"
                    }
                )
        return attrs


class OccupancySerializer(serializers.ModelSerializer):
    parking_lot_id = serializers.IntegerField(
        validators=[validate_parking_lot_id], help_text="ID of an existing parking lot."
    )
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Occupancy
        fields = ("id", "parking_lot_id", "occupied_spots", "timestamp")
