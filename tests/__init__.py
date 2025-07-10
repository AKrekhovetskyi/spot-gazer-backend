from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from faker import Faker

from livemap.models import Address, City, Country, ParkingLot, VideoStreamSource

if TYPE_CHECKING:
    from django.contrib.auth.models import UserManager

fake = Faker()


class TestCaseWithData:
    def setUp(self) -> None:
        # Set up data for the whole TestCase
        user_manager: UserManager = get_user_model().objects  # type: ignore[reportAssignmentType]
        self.username = fake.pystr()
        self.password = fake.pystr()
        self.user = user_manager.create_user(username=self.username, password=self.password)

        self.country = Country.objects.create(country_name=fake.country())
        self.city = City.objects.create(country=self.country, city_name=fake.city())
        self.address = Address.objects.create(city=self.city, parking_lot_address=fake.street_address())
        self.parking_lot = ParkingLot.objects.create(
            address=self.address,
            total_spots=fake.pyint(),
            spots_for_disabled=fake.pyint(),
            is_private=fake.random_element(ParkingLot.Answer.values),
            is_free=fake.random_element(ParkingLot.Answer.values),
            geolocation=[float(fake.latitude()), float(fake.longitude())],
        )
        self.stream_source_data = {
            "parking_lot": self.parking_lot,
            "stream_source": fake.url(),
            "processing_rate": fake.pyint(min_value=1, max_value=5),
            "is_active": True,
        }
        self.small_parking_lot = VideoStreamSource.objects.create(**self.stream_source_data)
        self.big_parking_lot = VideoStreamSource.objects.create(
            parking_lot=self.parking_lot,
            stream_source=fake.url(),
            processing_rate=self.small_parking_lot.processing_rate,
            is_active=True,
        )
