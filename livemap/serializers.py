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
    in_use_until = serializers.DateTimeField(read_only=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = VideoStreamSource
        fields = (
            "id",
            "parking_lot_address",
            "parking_lot_id",
            "stream_source",
            "processing_rate",
            "in_use_until",
            "is_active",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("processing_rate") and not attrs.get("parking_lot_id"):
            raise serializers.ValidationError(
                {
                    "parking_lot_id": "`parking_lot_id` field must be provided along with the `processing_rate` one",
                }
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> VideoStreamSource:
        parking_lot_id = validated_data.get("parking_lot_id")
        processing_rate = validated_data.get("processing_rate")
        if parking_lot_id and processing_rate:
            video_stream = VideoStreamSource.objects.filter(parking_lot=parking_lot_id).first()
            if video_stream and video_stream.processing_rate != processing_rate:
                raise serializers.ValidationError(
                    {
                        "processing_rate": [
                            f"The processing rate for the parking lot {parking_lot_id} "
                            f"must be {video_stream.processing_rate} seconds"
                        ]
                    }
                )
        return VideoStreamSource.objects.create(**validated_data)

    def update(self, instance: VideoStreamSource, validated_data: dict[str, Any]) -> VideoStreamSource:
        if (processing_rate := validated_data.get("processing_rate")) and processing_rate != instance.processing_rate:
            VideoStreamSource.objects.filter(parking_lot_id=validated_data["parking_lot_id"]).exclude(
                id=instance.pk
            ).update(processing_rate=processing_rate)
        return super().update(instance, validated_data)


class OccupancySerializer(serializers.ModelSerializer):
    parking_lot_id = serializers.IntegerField(
        validators=[validate_parking_lot_id], help_text="ID of an existing parking lot."
    )
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Occupancy
        fields = ("id", "parking_lot_id", "occupied_spots", "timestamp")
