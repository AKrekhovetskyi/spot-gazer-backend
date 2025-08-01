from datetime import UTC, datetime

from django.test import TestCase

from livemap.models import HourlyOccupancySummary, Occupancy
from livemap.tasks import aggregate_occupancy_and_delete_old_records
from tests import TestCaseWithData, fake


class CeleryTasksTest(TestCaseWithData, TestCase):
    def setUp(self) -> None:
        super().setUp()
        Occupancy.objects.all().delete()
        timestamps, occupancy_statistics = [], []
        self.avg_occupied_spots = set()
        self.aggregated_records = 0
        self.parking_lots = (self.parking_lot, self.another_parking_lot)
        for day, parking_lot in zip(range(1, 3), self.parking_lots, strict=True):
            for hour in range(1, 3):
                self.aggregated_records += 1
                spots_occupied = []
                for minute in range(10, 31, 10):
                    timestamps.append(datetime(year=2025, month=1, day=day, hour=hour, minute=minute, tzinfo=UTC))
                    occupied_spots = fake.pyint(min_value=0, max_value=100)
                    # Setting the `timestamp` manually will have no effect.
                    occupancy_statistics.append(Occupancy(parking_lot=parking_lot, occupied_spots=occupied_spots))
                    spots_occupied.append(occupied_spots)
                self.avg_occupied_spots.add(round(sum(spots_occupied) / len(spots_occupied)))
        saved_statistics = Occupancy.objects.bulk_create(occupancy_statistics)
        for occupancy, timestamp in zip(saved_statistics, timestamps, strict=True):
            occupancy.timestamp = timestamp
            occupancy.save()

    def test_aggregate_occupancy_and_delete_old_records(self) -> None:
        aggregate_occupancy_and_delete_old_records()
        aggregations = HourlyOccupancySummary.objects.all()
        self.assertEqual(len(aggregations), self.aggregated_records)
        self.assertSetEqual(self.avg_occupied_spots, {aggregation.avg_occupied_spots for aggregation in aggregations})
        self.assertEqual(Occupancy.objects.count(), len(self.parking_lots))

        # Make sure there are no duplicate records in the table after a second aggregation.
        aggregate_occupancy_and_delete_old_records()
        self.assertEqual(HourlyOccupancySummary.objects.count(), len(aggregations))
