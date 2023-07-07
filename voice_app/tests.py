
from __future__ import annotations

# movies/tests/twilio_phone_call.py
import pytest
from . import const
from .test_funcs import TwilioPhoneCall, phone_call, django_db_setup, db_access_without_rollback_and_truncate
from .funcs import NOT_MODEL, NOT_MARKA, NOT_3_ROK, NOT_ROK, CORRECT

@pytest.mark.django_db
def test_options(
    phone_call: TwilioPhoneCall,
    db: db
) -> None:
    """ Test if options work

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
Informacje_dobrze: koniec
Powtórzenie_informacji: Zgadza się
"""
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

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
        dodatkowe_informacje="koniec",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'Zgadza się' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][10][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'O co mogłabym jeszczę poprosić?' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({ 'SpeechResult': 'Koniec' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_repeat(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if repeat works """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content
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
    assert const.PREPARED_TEXT["CANCEL"].format(flow="zapis") in content
    response = phone_call._make_request({ 'SpeechResult': 'Powtórz' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["CANCEL"].format(flow="zapis") in content
    response = phone_call._make_request({ 'SpeechResult': 'Tak' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

@pytest.mark.django_db
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
Informacje_dobrze: koniec
Powtórzenie_informacji: koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

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
        dodatkowe_informacje="koniec",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][10][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'To wszystko' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_wiadomosci_client_1(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if wiadomosci works

CLIENT
------
imie_nazwisko: Jan Kowalski
wiadomość: Czy mogę przyjechać wcześniej na wymianę świec?
numer_telefonu: 123456789
Informacje_dobrze: Koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({
        'SpeechResult': '''Chciałbym się zapytać Pani Pauliny czy mógłbymprzyjechać wcześniej na wymianę świec?'''
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Jan Kowalski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][1][0] in content

    response = phone_call._make_request({
        'SpeechResult': 'Czy mogę przyjechać wcześniej na wymianę świec?'
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': '123456789' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][3][0].format(
        imie_nazwisko="Jan Kowalski",
        wiadomość="Czy mogę przyjechać wcześniej na wymianę świec?",
        numer_telefonu="123456789",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'Koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][4][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'To będzię na tyle' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_wiadomosci_zapisu_client_1(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if wiadomosci i zapisu w jednej konwersacji

CLIENT
------
zapis: Przegląd auta
nowy_klient: Nie
imie_nazwisko: Robert Falkowski
numer_telefonu: 728898380
numer_rejestracyjny: WA7959E
marka: Lexus
model: IS200
rok_produkcji: 2003
dodatkowe_informacje: koniec
Informacje_dobrze: koniec
imie_nazwisko: Robert Falkowski
wiadomość:
    Chciałbym się zapytać czy mógłbym przy okazji
    zostawienia mojego lexusa odebrać rx400,
    który jest u Państwa na serwisie?
numer_telefonu: 728898380
Informacje_dobrze: koniec """

    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({ 'SpeechResult': 'Przegląd auta' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Przegląd auta' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][1][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Nie' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Robert Falkowski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][3][0] in content

    response = phone_call._make_request({ 'SpeechResult': '728898380' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][4][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'WA7958E' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][5][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'LEXUS' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][6][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'IS200' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][7][0] in content

    response = phone_call._make_request({ 'SpeechResult': '2003' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][8][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][9][0].format(
        zapis="Przegląd auta",
        nowy_klient=True,
        imie_nazwisko="Robert Falkowski",
        numer_telefonu="728898380",
        numer_rejestracyjny="WA7958E",
        marka="lexus",
        model="IS 200",
        rok_produkcji="2003",
        dodatkowe_informacje="koniec",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][10][0] in content

    response = phone_call._make_request({
        'SpeechResult': '''Chciałbym się zapytać czy mógłbym przy okazji zostawienia mojego lexusa odebrać rx400, który jest u Państwa na serwisie?'''
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Robert Falkowski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][1][0] in content

    response = phone_call._make_request({
        'SpeechResult': "Chciałbym się zapytać czy mógłbym przy okazji zostawienia mojego lexusa odebrać rx400, który jest u Państwa na serwisie?"
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': '728898380' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][3][0].format(
        imie_nazwisko="Robert Falkowski",
        wiadomość="Chciałbym się zapytać czy mógłbym przy okazji zostawienia mojego lexusa odebrać rx400, który jest u Państwa na serwisie?",
        numer_telefonu="728898380",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][4][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'to tyle' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_zapis_wrong_car(
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
Informacje_dobrze: koniec
Powtórzenie_informacji: koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

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

    response = phone_call._make_request({ 'SpeechResult': 'Subaru' })
    content = response.content.decode()
    assert NOT_MARKA.format(
        marka="Subaru",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'Leksus' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][6][0] in content
    
    response = phone_call._make_request({ 'SpeechResult': 'RX 220' })
    content = response.content.decode()
    assert NOT_MODEL.format(
        marka="lexus",
        model="RX 220",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'RX 310' })
    content = response.content.decode()
    assert NOT_MODEL.format(
        marka="lexus",
        model="RX 310",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'RX 300' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][7][0] in content

    response = phone_call._make_request({ 'SpeechResult': '1980' })
    content = response.content.decode()
    assert NOT_ROK.format(
        marka="lexus",
        model="RX 300",
        rok_produkcji="1980",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': '1981' })
    content = response.content.decode()
    assert NOT_ROK.format(
        marka="lexus",
        model="RX 300",
        rok_produkcji="1981",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': '1982' })
    content = response.content.decode()
    assert NOT_3_ROK.format(
        marka="lexus",
        model="RX 300",
        rok_produkcji="1982",
    ) in content
    assert "Hangup" in content
    

@pytest.mark.django_db
def test_anuluj_wiadomosc(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if wiadomosci works

CLIENT
------
imie_nazwisko: Jan Kowalski
wiadomość: Czy mogę przyjechać wcześniej na wymianę świec?
numer_telefonu: 123456789
Informacje_dobrze: Koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({
        'SpeechResult': '''Chciałbym się zapytać Pani Pauliny czy mógłbymprzyjechać wcześniej na wymianę świec?'''
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Jan Kowalski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][1][0] in content

    response = phone_call._make_request({
        'SpeechResult': 'Czy mogę przyjechać wcześniej na wymianę świec?'
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'anuluj wiadomość' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["CANCEL"].format(flow="wiadomość") in content

    response = phone_call._make_request({ 'SpeechResult': 'tak' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({ 'SpeechResult': 'koniec' })
    content = response.content.decode()
    assert "Hangup" in content


@pytest.mark.django_db
def test_anuluj_zapis(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    """ Test if wiadomosci works

CLIENT
------
imie_nazwisko: Jan Kowalski
wiadomość: Czy mogę przyjechać wcześniej na wymianę świec?
numer_telefonu: 123456789
Informacje_dobrze: Koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

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

    response = phone_call._make_request({ 'SpeechResult': 'anuluj zapis' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["CANCEL"].format(flow="zapis") in content

    response = phone_call._make_request({ 'SpeechResult': 'tak' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({ 'SpeechResult': 'To wszystko' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_correct_zapis(
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
Informacje_dobrze: koniec
Powtórzenie_informacji: koniec """
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

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
        dodatkowe_informacje="koniec",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'tak' })
    content = response.content.decode()
    assert CORRECT in content

    response = phone_call._make_request({ 'SpeechResult': 'Zamiast na wymiane oleju, chciałem się zapisać na przegląd auta oraz mój numer rejestracyjny ma na końcu literę i, a nie a.' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][9][0].format(
        zapis="Przegląd auta",
        nowy_klient=False,
        imie_nazwisko="Jan Kowalski",
        numer_telefonu="123456789",
        numer_rejestracyjny="WA7959I",
        marka="toyota",
        model="RAV4",
        rok_produkcji="2001",
        dodatkowe_informacje="koniec",
    ) in content


    response = phone_call._make_request({ 'SpeechResult': 'nie' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["ZAPIS"][10][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'To wszystko' })
    content = response.content.decode()
    assert "Hangup" in content

@pytest.mark.django_db
def test_correct_wiadomosc(
    phone_call: TwilioPhoneCall,
    db: db
    ) -> None:
    response = phone_call.initiate()
    content = response.content.decode()
    assert const.PREPARED_TEXT["PRESENT PROMPTS"] in content

    response = phone_call._make_request({
        'SpeechResult': '''Chciałbym się zapytać, kiedy mógłbym odebrać auto po wymianie opon.'''
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][0][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Jan Kowalski' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][1][0] in content

    response = phone_call._make_request({
        'SpeechResult': "Kiedy mogę odebrać auto po wymianie opon?"
    })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][2][0] in content

    response = phone_call._make_request({ 'SpeechResult': '123456789' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][3][0].format(
        imie_nazwisko="Jan Kowalski",
        wiadomość="Kiedy mogę odebrać auto po wymianie opon?",
        numer_telefonu="123456789",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'Tak' })
    content = response.content.decode()
    assert CORRECT in content

    response = phone_call._make_request({ 'SpeechResult': 'Mój numer to 1 2 3 4 5 6 7 8 8' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][3][0].format(
        imie_nazwisko="Jan Kowalski",
        wiadomość="Kiedy mogę odebrać auto po wymianie opon?",
        numer_telefonu="123456788",
    ) in content

    response = phone_call._make_request({ 'SpeechResult': 'Nie' })
    content = response.content.decode()
    assert const.PREPARED_TEXT["WIADOMOŚĆ"][4][0] in content

    response = phone_call._make_request({ 'SpeechResult': 'Dziękuje, to wszystko' })
    content = response.content.decode()
    assert "Hangup" in content
