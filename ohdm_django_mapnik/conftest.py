import pytest
from django.conf import settings
from django.test import RequestFactory


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
