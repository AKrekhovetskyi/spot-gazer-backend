from http import HTTPStatus
from io import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from livemap.views import _compose_html_table, _extract_client_ip_address, _fetch_geolocation
from tests import TestCaseWithData, fake


class HelperFunctionsTest(TestCase):
    def test__extract_client_ip_address(self) -> None:
        fake_ip = fake.ipv4()
        meta = {"REMOTE_ADDR": fake_ip, "REQUEST_METHOD": "GET", "wsgi.input": StringIO()}
        ip_by_remote_addr = _extract_client_ip_address(WSGIRequest(meta))  # pyright: ignore[reportCallIssue]
        self.assertEqual(ip_by_remote_addr, fake_ip)

        ip_by_http_x_forwarded = _extract_client_ip_address(WSGIRequest(meta | {"HTTP_X_FORWARDED_FOR": fake_ip}))  # pyright: ignore[reportCallIssue]
        self.assertEqual(ip_by_http_x_forwarded, fake_ip)

    @parameterized.expand([(fake.pystr(), type(None)), (fake.ipv4(), tuple)])
    def test__fetch_geolocation(self, ip_address: str, return_type: type[None] | tuple) -> None:
        self.assertIsInstance(_fetch_geolocation(ip_address), return_type)


class ViewsTest(TestCaseWithData, TestCase):
    def test__compose_html_table(self) -> None:
        html_table = _compose_html_table(self.parking_lot)
        for field in ("Address", "Private", "Free", "Total spots", "Spots for disables", "Free spots"):
            self.assertIn(field, html_table)
        self.assertIn(
            "<a href='https://www.google.com/maps/search/?api=1&query="
            f"{self.parking_lot.latitude},{self.parking_lot.longitude}'>{self.parking_lot.address}</a>",
            html_table,
        )
        for stream_source in self.parking_lot.stream_sources.filter(parking_lot_id=self.parking_lot.pk):  # pyright: ignore[reportAttributeAccessIssue]
            self.assertIn(stream_source.stream_source, html_table)

    def test_index(self) -> None:
        response = self.client.get(reverse("livemap:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
