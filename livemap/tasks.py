from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.db.models import Avg, Max
from django.db.models.functions import TruncDate, TruncHour

from .models import HourlyOccupancySummary, Occupancy

logger = get_task_logger(__name__)


@shared_task(name="Aggregate occupancy and delete old records")
def aggregate_occupancy_and_delete_old_records() -> None:
    """Aggregate occupancy statistics by hours and delete old records to free up space.
    Remove all but the newest Occupancy records per `parking_lot`.
    """
    aggregated_occupancy = (
        Occupancy.objects.annotate(date=TruncDate("timestamp"), hour=TruncHour("timestamp"))
        .values("parking_lot", "date", "hour")
        .annotate(avg_occupied_spots=Avg("occupied_spots"))
    )

    # Remove all but the newest Occupancy records per parking_lot.
    # Step 1: Get the latest timestamp per parking lot.
    latest_per_lot = Occupancy.objects.values("parking_lot").annotate(latest=Max("timestamp"))

    # Step 2: Build a set of IDs of the newest records to preserve.
    latest_ids = set(
        Occupancy.objects.filter(
            parking_lot__in=[entry["parking_lot"] for entry in latest_per_lot],
            timestamp__in=[entry["latest"] for entry in latest_per_lot],
        ).values_list("id", flat=True)
    )

    with transaction.atomic(durable=True):
        occupancy_summary_count = 0
        for item in aggregated_occupancy:
            hour = item["hour"].hour
            date = item["date"].isoformat()
            if not HourlyOccupancySummary.objects.filter(
                parking_lot_id=item["parking_lot"], hour=hour, date=date
            ).exists():
                HourlyOccupancySummary.objects.create(
                    parking_lot_id=item["parking_lot"],
                    avg_occupied_spots=round(item["avg_occupied_spots"]),
                    hour=hour,
                    date=date,
                )
                occupancy_summary_count += 1
        # Step 3: Delete all other records.
        count, _ = Occupancy.objects.exclude(id__in=latest_ids).delete()
    logger.info("Inserted %s occupancy aggregations", occupancy_summary_count)
    logger.info("Deleted %s old occupancy records. %s newest left", count, len(latest_ids))
