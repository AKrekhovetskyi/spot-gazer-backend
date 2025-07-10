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
        elements_number = 1
        self.assertEqual(len(response.json()), elements_number)
        streams_number = 2
        self.assertEqual(len(response.json()[0]["streams"]), streams_number)

    def test_post_method(self) -> None:
        fake_stream = {
            "parking_lot_id": self.parking_lot.pk,
            "stream_source": fake.url(),
            "processing_rate": self.stream_source_data["processing_rate"],
            "is_active": fake.pybool(),
        }
        self.client.login(username=self.username, password=self.password)
        request = self.client.post(self.video_stream_path, content_type=CONTENT_TYPE, data=fake_stream)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(request.json()["stream_source"], fake_stream["stream_source"])

    def test_filters(self) -> None:
        response = self.client.get(self.video_stream_path, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        VideoStreamSource.objects.filter(pk=self.big_parking_lot.pk).update(is_active=False)
        filtered_response = self.client.get(f"{self.video_stream_path}?active_only=true", content_type=CONTENT_TYPE)
        self.assertEqual(len(response.json()[0]["streams"]) - 1, len(filtered_response.json()))


class OccupancyTests(TestCaseWithData, APITestCase):
    occupancy_path = "/api/occupancy/"

    def test_get_method(self) -> None:
        response = self.client.get(self.occupancy_path, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        elements_number = 2
        self.assertEqual(len(response.json()), elements_number)

    def test_post_method(self) -> None:
        occupancy = {"parking_lot_id": self.parking_lot.pk, "occupied_spots": fake.pyint(min_value=1)}
        response = self.client.post(self.occupancy_path, content_type=CONTENT_TYPE, data=occupancy)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.occupancy_path, content_type=CONTENT_TYPE, data=occupancy)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
