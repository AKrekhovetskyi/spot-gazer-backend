from typing import Any

from django.db.models import Model
from rest_framework import serializers

from .models import Occupancy, ParkingLot, VideoStreamSource


class CreateMixin:
    class Meta:
        model: Model

    def create(self, validated_data: dict[str, Any]) -> Model:
        parking_lot_id = validated_data.get("parking_lot_id")
        if parking_lot_id and not ParkingLot.objects.filter(id=parking_lot_id).first():
            raise serializers.ValidationError(
                {"parking_lot_id": f"Parking lot with the {parking_lot_id} ID not found."}
            )
        return self.Meta.model.objects.create(**validated_data)


class VideoStreamSourceSerializer(CreateMixin, serializers.ModelSerializer):
    parking_lot_address = serializers.CharField(source="parking_lot.address", read_only=True)
    parking_lot_id = serializers.IntegerField(help_text="ID of an existing parking lot.")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = VideoStreamSource
        fields = ("id", "parking_lot_address", "parking_lot_id", "stream_source", "processing_rate", "is_active")


class OccupancySerializer(CreateMixin, serializers.ModelSerializer):
    parking_lot_id = serializers.IntegerField(help_text="ID of an existing parking lot.")
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Occupancy
        fields = ("id", "parking_lot_id", "occupied_spots", "timestamp")
