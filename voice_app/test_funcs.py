from __future__ import annotations
from typing import Optional, Iterator, Dict, Any

from django.http import HttpResponse
from xml.etree import ElementTree
from django.test.client import Client

from django.urls import reverse
from unittest import mock
import pytest
from . import const

@pytest.fixture(scope='session')
def django_db_setup():
    """Avoid creating/setting up the test database"""
    pass

@pytest.fixture
def db_access_without_rollback_and_truncate(request, django_db_setup, django_db_blocker):
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.restore)


@pytest.mark.django_db
class TwilioPhoneCall:

    def __init__(
        self,
        start_url: str,
        call_sid: str,
        from_number: str,
        client: Client,
    ) -> None:
        self.next_url: Optional[str] = start_url
        self.call_sid = call_sid
        self.from_number = from_number
        self.client = client
        self.call_ended = False
        self._current_twiml_response: Optional[Iterator[Optional[HttpResponse]]] = None

    def _make_request(self, payload: Dict[str, Any] = {}) -> Optional[HttpResponse]:
        assert self.next_url is not None
        with mock.patch('voice_app.views.request_validator', autospec=True) as gather_answer_mock:
            gather_answer_mock.validate.return_value = True
            response = self.client.post(self.next_url, {
                'CallSid': self.call_sid,
                'From': self.from_number,
                **payload,
            }, HTTP_X_TWILIO_SIGNATURE='signature')

        self._current_twiml_response = self._process_twiml_response(response)
        return next(self._current_twiml_response)

    def initiate(self) -> HttpResponse:
        return self._make_request()

    def _process_twiml_response(self, response: HttpResponse) -> Iterator[Optional[HttpResponse]]:
        if not 200 <= response.status_code < 300:
            self.call_ended = True
            self.next_url = None
            yield response
            return

        # Find the next action to perform
        tree = ElementTree.fromstring(response.content.decode())
        for element in tree:
            if element.tag == 'Hangup':
                self.call_ended = True
                yield response

            elif element.tag == 'Redirect':
                if element.text is None:
                    # An empty <Redirect> implies current URL.
                    self.next_url = response.wsgi_request.get_full_path()
                else:
                    self.next_url = element.text
                yield self._make_request()

            elif element.tag == 'Gather':
                self.next_url = element.get('action')
                yield response

@pytest.fixture
def phone_call(client: Client) -> TwilioPhoneCall:
    return TwilioPhoneCall(
        start_url = reverse('greet_client'),
        client = client,
        call_sid = 'call-sid-1',
        from_number = '123456789',
    )