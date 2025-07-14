from copy import deepcopy
from datetime import UTC, datetime, timedelta
from time import sleep

from rest_framework import status
from rest_framework.test import APITestCase

from livemap.models import VideoStreamSource
from tests import TestCaseWithData, fake

CONTENT_TYPE = "application/json"


class VideoStreamSourceTests(TestCaseWithData, APITestCase):
    video_stream_path = "/api/video-stream-sources/"

    def test_get_method(self) -> None:
        response = self.client.get(self.video_stream_path, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results_number = 1
        self.assertEqual(len(response.json()["results"]), results_number, msg=response.json())
        streams_number = 2
        self.assertEqual(len(response.json()["results"][0]["streams"]), streams_number)

    def test_post_method(self) -> None:
        fake_stream = {
            "parking_lot_id": self.parking_lot.pk,
            "stream_source": fake.url(),
            "processing_rate": self.stream_source_data["processing_rate"],
            "is_active": fake.pybool(),
        }
        self.client.login(username=self.username, password=self.password)
        request = self.client.post(self.video_stream_path, content_type=CONTENT_TYPE, data=fake_stream)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED, msg=request.json())
        self.assertEqual(request.json()["stream_source"], fake_stream["stream_source"])

        fake_stream_copy = deepcopy(fake_stream)
        fake_parking_lot_id = fake.pyint(min_value=10)
        fake_stream_copy["parking_lot_id"] = fake_parking_lot_id
        request = self.client.post(self.video_stream_path, content_type=CONTENT_TYPE, data=fake_stream_copy)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            request.json()["parking_lot_id"][0], f"No parking lot found for the provided ID {fake_parking_lot_id}"
        )

        fake_stream_copy = deepcopy(fake_stream)
        processing_rate = VideoStreamSource.ProcessingRate.values
        processing_rate.remove(self.stream_source_data["processing_rate"])
        fake_stream_copy["processing_rate"] = fake.random_element(processing_rate)
        request = self.client.post(self.video_stream_path, content_type=CONTENT_TYPE, data=fake_stream_copy)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The processing rate for the parking lot", request.json()["processing_rate"][0])

    def test_patch_method(self) -> None:
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(f"{self.video_stream_path}1/", content_type=CONTENT_TYPE)
        self.assertEqual(response.json()["is_active"], True)
        response = self.client.patch(
            f"{self.video_stream_path}1/", content_type=CONTENT_TYPE, data={"id": 1, "is_active": False}
        )
        response = self.client.get(f"{self.video_stream_path}1/", content_type=CONTENT_TYPE)
        self.assertEqual(response.json()["is_active"], False)

        processing_rate = VideoStreamSource.ProcessingRate.values
        processing_rate.remove(self.stream_source_data["processing_rate"])
        response = self.client.patch(
            f"{self.video_stream_path}1/",
            content_type=CONTENT_TYPE,
            data={"id": 1, "processing_rate": fake.random_element(processing_rate)},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["parking_lot_id"][0],
            "`parking_lot_id` field must be provided along with the `processing_rate` one",
        )

    def test_active_only_filter(self) -> None:
        response = self.client.get(self.video_stream_path, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        VideoStreamSource.objects.filter(pk=self.big_parking_lot.pk).update(is_active=False)
        filtered_response = self.client.get(
            self.video_stream_path, content_type=CONTENT_TYPE, query_params={"active_only": True}
        )
        self.assertEqual(
            len(response.json()["results"][0]["streams"]) - 1,
            len(filtered_response.json()["results"][0]["streams"]),
            msg=f"{response.json()=} {filtered_response.json()=}",
        )

    def test_mark_in_use_until_filter(self) -> None:
        self.client.login(username=self.username, password=self.password)

        delta_seconds = timedelta(seconds=2)
        in_use_until = (datetime.now(UTC) + delta_seconds).isoformat()
        response = self.client.get(
            f"{self.video_stream_path}", content_type=CONTENT_TYPE, query_params={"mark_in_use_until": in_use_until}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

        # All returned streams should have `in_use_until` set to the requested value
        for group in response.json()["results"]:
            for stream in group["streams"]:
                self.assertEqual(datetime.fromisoformat(stream["in_use_until"]), datetime.fromisoformat(in_use_until))

        # All streams are in use. Nothing is returned.
        in_use_until = (datetime.now(UTC) + delta_seconds).isoformat()
        response = self.client.get(
            f"{self.video_stream_path}", content_type=CONTENT_TYPE, query_params={"mark_in_use_until": in_use_until}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(response.json(), {"count": 0, "next": None, "previous": None, "results": []})

        sleep(delta_seconds.seconds)
        in_use_until = (datetime.now(UTC) + delta_seconds).isoformat()
        response = self.client.get(
            f"{self.video_stream_path}", content_type=CONTENT_TYPE, query_params={"mark_in_use_until": in_use_until}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertNotEqual(response.json(), [])


class OccupancyTests(TestCaseWithData, APITestCase):
    occupancy_path = "/api/occupancy/"

    def test_get_method(self) -> None:
        response = self.client.get(self.occupancy_path, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        elements_number = 2
        self.assertEqual(response.json()["count"], elements_number)

    def test_post_method(self) -> None:
        occupancy = {"parking_lot_id": self.parking_lot.pk, "occupied_spots": fake.pyint(min_value=1)}
        response = self.client.post(self.occupancy_path, content_type=CONTENT_TYPE, data=occupancy)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.occupancy_path, content_type=CONTENT_TYPE, data=occupancy)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
