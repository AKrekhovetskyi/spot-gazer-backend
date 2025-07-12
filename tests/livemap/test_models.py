from django.test import TestCase

from livemap.models import ParkingLot
from tests import TestCaseWithData


class ParkingLotModelTest(TestCaseWithData, TestCase):
    def test_parking_lot_choices(self) -> None:
        self.assertIn(self.parking_lot.get_is_private, ParkingLot.Answer.labels)
        self.assertIn(self.parking_lot.get_is_free, ParkingLot.Answer.labels)
