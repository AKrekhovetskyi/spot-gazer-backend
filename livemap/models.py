from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Country(models.Model):
    country_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return str(self.country_name)


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    city_name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return f"{self.city_name}, {self.country}"


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="addresses")
    parking_lot_address = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self) -> str:
        return f"{self.parking_lot_address}, {self.city}"


class ParkingLot(models.Model):
    class Answer(models.IntegerChoices):
        NO = 0, "No"
        YES = 1, "Yes"

    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="parking_lots", related_query_name="parking_lot"
    )
    total_spots = models.PositiveIntegerField()
    spots_for_disabled = models.PositiveIntegerField(null=True, blank=True)
    is_private = models.IntegerField(choices=Answer.choices, default=Answer.NO)
    is_free = models.IntegerField(choices=Answer.choices, default=Answer.YES)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)], null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)], null=True
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
    class ProcessingRate(models.IntegerChoices):
        FIVE = 5, "5 seconds"
        TEN = 10, "10 seconds"
        THIRTY = 30, "30 seconds"
        SIXTY = 60, "60 seconds"
        ONE_HUNDRED_TWENTY = 120, "120 seconds"
        ONE_HUNDRED_EIGHTY = 180, "180 seconds"

    parking_lot = models.ForeignKey(
        ParkingLot, on_delete=models.CASCADE, related_name="stream_sources", related_query_name="stream_source"
    )
    stream_source = models.URLField()
    processing_rate = models.PositiveIntegerField(
        choices=ProcessingRate, help_text="In seconds. The same for all video streams from the same parking lot."
    )
    is_active = models.BooleanField(default=True)

    # The fields below are for internal services only!
    in_use_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time in UTC timezone until the video stream is in use.",
    )

    def __str__(self) -> str:
        return f"{self.stream_source}, {self.parking_lot}"


class Occupancy(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="occupancies")
    occupied_spots = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "timestamp"
        verbose_name_plural = "occupancy"

    def __str__(self) -> str:
        return f"{self.occupied_spots} occupied spots, {self.parking_lot}"
