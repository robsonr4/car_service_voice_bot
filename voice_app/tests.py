
# movies/tests/twilio_phone_call.py
from __future__ import annotations
from typing import Optional, Iterator, Dict, Any

from django.http import HttpResponse
from xml.etree import ElementTree
from django.test.client import Client

# movies/tests/twilio_phone_call.py
from django.urls import reverse
from unittest import mock
import pytest
from . import const

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
        start_url = reverse('gather_answer'),
        client = client,
        call_sid = 'call-sid-1',
        from_number = '123456789',
    )

def test_repeat(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if repeat works """
    response = phone_call.initiate()
    content = response.content.decode()
    response = phone_call._make_request({ 'SpeechResult': 'Chciałbym się zapisać na wymianę oleju' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][0][0] in content
    response = phone_call._make_request({ 'SpeechResult': 'Powtórz' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][0][0] in content
    response = phone_call._make_request({ 'SpeechResult': 'Wymiana oleju' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][1][0] in content
    response = phone_call._make_request({ 'SpeechResult': 'Anuluj zapis' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["CANCEL"].format(flow="ZAPIS") in content
    response = phone_call._make_request({ 'SpeechResult': 'Powtórz' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["CANCEL"].format(flow="ZAPIS") in content
    response = phone_call._make_request({ 'SpeechResult': 'Tak' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content


def test_zapis_client_1(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if zapis works

CLIENT
------
zapis: Wymiana oleju
nowy_klient: Tak
imie_nazwisko: Jan Kowalski
numer_telefonu: 123456789
numer_rejestracyjny: WA7959E
marka: Toyota
model: RAV4
rok_produkcji: 2001
dodatkowe_informacje: koniec
Powtórzenie_informacji: koniec """
    response = phone_call.initiate()

    response = phone_call._make_request({ 'SpeechResult': 'Zapis na wymiane oleju' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Wymiana oleju' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][1][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Tak' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Jan Kowalski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][3][0] in content

    response = phone_call._make_request({ 'SpeechResult': '123456789' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][4][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'WA7959E' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][5][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Toyota' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][6][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'RAV4' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][7][0] in content

    response = phone_call._make_request({ 'SpeechResult': '2001' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][8][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][9][0].format(
        zapis="Wymiana oleju",
        nowy_klient=False,
        imie_nazwisko="Jan Kowalski",
        numer_telefonu="123456789",
        numer_rejestracyjny="WA7959E",
        marka="toyota",
        model="RAV4",
        rok_produkcji="2001",
        dodatkowe_informacje="",
    ) in content
