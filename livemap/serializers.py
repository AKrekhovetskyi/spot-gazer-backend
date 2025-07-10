from typing import Any

from rest_framework import serializers

from .models import ParkingLot, VideoStreamSource


class VideoStreamSourceSerializer(serializers.ModelSerializer):
    parking_lot_address = serializers.CharField(source="parking_lot.address", read_only=True)
    parking_lot_id = serializers.IntegerField(help_text="ID of an existing parking lot.")

    class Meta:
        model = VideoStreamSource
        fields = ("id", "parking_lot_address", "parking_lot_id", "stream_source", "processing_rate", "is_active")

    def create(self, validated_data: dict[str, Any]) -> VideoStreamSource:
        parking_lot_id = validated_data.get("parking_lot_id")
        if parking_lot_id and not ParkingLot.objects.filter(id=parking_lot_id).first():
            raise serializers.ValidationError(
                {"parking_lot_id": f"Parking lot with the {parking_lot_id} ID not found."}
            )
        return VideoStreamSource.objects.create(**validated_data)
