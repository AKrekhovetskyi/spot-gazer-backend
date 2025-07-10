from rest_framework import status
from rest_framework.test import APITestCase

from livemap.models import VideoStreamSource
from livemap.serializers import VideoStreamSourceSerializer
from tests import TestCaseWithData, fake


class VideoStreamSourceTests(TestCaseWithData, APITestCase):
    video_stream_path = "/api/video-stream-sources/"
    content_type = "application/json"

    def test_get_method(self) -> None:
        response = self.client.get(self.video_stream_path, content_type=self.content_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        elements_number = 2
        self.assertEqual(len(response.json()), elements_number)
        for stream in response.json():
            self.assertEqual(VideoStreamSourceSerializer.Meta.fields, tuple(stream))

    def test_post_method(self) -> None:
        fake_stream = {
            "parking_lot_id": self.parking_lot.pk,
            "stream_source": fake.url(),
            "processing_rate": self.stream_source_data["processing_rate"],
            "is_active": fake.pybool(),
        }
        self.client.login(username=self.username, password=self.password)
        request = self.client.post(self.video_stream_path, content_type=self.content_type, data=fake_stream)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(request.json()["stream_source"], fake_stream["stream_source"])

    def test_filters(self) -> None:
        response = self.client.get(self.video_stream_path, content_type=self.content_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        VideoStreamSource.objects.filter(pk=self.big_parking_lot.pk).update(is_active=False)
        filtered_response = self.client.get(
            f"{self.video_stream_path}?active_only=true", content_type=self.content_type
        )
        self.assertEqual(len(response.json()) - 1, len(filtered_response.json()))
