from typing import Any

from django.core.exceptions import ValidationError
from django.db import models


class Country(models.Model):
    country_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return str(self.country_name)


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    city_name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self) -> str:
        return f"{self.city_name}, {self.country}"


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="addresses")
    parking_lot_address = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self) -> str:
        return f"{self.parking_lot_address}, {self.city}"


def validate_geolocation(geolocation: Any) -> None:
    # TODO @AKrekhovetskyi: Use separate fields for latitude and longitude.  # noqa: FIX002
    # https://github.com/AKrekhovetskyi/spot-gazer/issues/28
    if not isinstance(geolocation, list) or len(geolocation) != 2:  # noqa: PLR2004
        raise ValidationError("The geolocation value must be a list of 2 integers or floating-point numbers!")
    if not all(isinstance(location, (int, float)) for location in geolocation):
        raise ValidationError("Both values must be either integers or floating-point numbers!")
    if not (-90 <= geolocation[0] <= 90) or not (-180 <= geolocation[1] <= 180):  # noqa: PLR2004
        raise ValidationError(
            "The latitude should be in the range [-90, 90] and the longitude should be in the range [-180, 180]"
        )


class ParkingLot(models.Model):
    class Answer(models.IntegerChoices):
        NO = 0, "No"
        YES = 1, "Yes"

    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="parking_lots")
    total_spots = models.PositiveIntegerField()
    spots_for_disabled = models.PositiveIntegerField(null=True, blank=True)
    is_private = models.IntegerField(choices=Answer.choices, default=Answer.NO)
    is_free = models.IntegerField(choices=Answer.choices, default=Answer.YES)
    geolocation = models.JSONField(
        validators=[validate_geolocation],
        help_text="Latitude and longitude of a parking lot. Ex.: [49.911848, 16.611212]",
    )

    def __str__(self) -> str:
        return str(self.address)

    @property
    def get_is_private(self) -> str:
        # Get label from choices enum.
        is_private_index = self.Answer.values.index(self.is_private)
        return self.Answer.labels[is_private_index]  # pyright: ignore[reportReturnType]

    @property
    def get_is_free(self) -> str:
        is_free_index = self.Answer.values.index(self.is_free)
        return self.Answer.labels[is_free_index]  # pyright: ignore[reportReturnType]


class VideoStreamSource(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="stream_sources")
    stream_source = models.URLField()
    processing_rate = models.PositiveIntegerField(
        help_text="In seconds. The same for all video streams from the same parking lot."
    )
    parking_zone = models.JSONField(
        blank=True, null=True, help_text="An array in a format [[[[int, int]], [[int, int]], ...]]."
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.stream_source}, {self.parking_lot}"


class Occupancy(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="occupancies")
    occupied_spots = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "timestamp"
        verbose_name_plural = "Occupancy"

    def __str__(self) -> str:
        return f"{self.occupied_spots} occupied spots, {self.parking_lot}"
