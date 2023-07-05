from .funcs import cancel, end

PROMPTS = {
    "GENERAL": {
        "role": "system",
        "content": """Jesteś wirtualnym asystentem serwisu samochodowego Lexusa, Toyoty. Bądź konkretny. Przywitaj się tylko raz. Twoim zadaniami są:
- Zapisanie klienta na przegląd;
- Odpowiedzenie o zapytanie o cenę podstawowych usług serwisowych;
- Przekazanie rozmowy do konsultanta, jeżeli klient dzwoni w innej sprawie niż z tych, co wymienione."""
    },
    "PRZEGLAD": {
        "role": "system",
        "content": """Nie witaj się ponownie. Poproś klienta pojedynczo o imię i nazwisko, numer telefonu, numer rejestracyjny samochodu, model samochodu, rok produkcji samochodu, przebieg samochodu, dodatkowe informacje."""
    }
}

PREPARED_TEXT = {
    "PRESENT PROMPTS": """Możesz mnie poprosić o.: zapisanie na jedną lub więcej usług,
        lub o przekazanie wiadomości dla konsultanta.""",
    "GREET CLIENT": """Cześć, to jest automatyczna sekretarka serwisu Lexusa, Toyoty.
        Jak mogłabym Państwu dzisiaj pomóc?""",
    "CANCEL": "Czy na pewno chcą państwo anulować {flow}?",
    "ZAPIS": [
        ("""Zrozumiałam, że chcą Państwo się zapisać na serwis. W każdym momencie mogą Państwo
            powiedzieć 'anuluj zapis', a w takim wypadku wszystkie zapisane informacje zostaną
            usunięte. Na początku chciałabym się zapytać, na jaką usługę lub usługi chcieliby
            Państwo się zapisać?""", "zapis", [cancel]),
        ("""Dziękuję. Chciałabym się zapytać, czy Państwo już byli u nas w serwisie? Proszę
            odpowiedzieć 'tak' lub 'nie'.""", "nowy_klient", [cancel]),
        ("Dziękuję. Poprosiłabym Państwa o imię i nazwisko.", "imie_nazwisko", [cancel]),
        ("Dziękuję. Proszę podać swój numer telefonu.", "numer_telefonu", [cancel]),
        ("Dziękuję. Proszę powoli przeliterować numer rejestracyjny samochodu.", "numer_rejestracyjny", [cancel]),
        ("Dziękuję. Prosze podać markę samochodu.", "marka", [cancel]),
        ("Dziękuję. Proszę podać model samochodu.", "model", [cancel]),
        ("Dziękuję. Proszę podać rok produkcji samochodu.", "rok_produkcji", [cancel]),
        ("""Dziękuję. Proszę podać dodatkowe informacje, jeżeli takie są. W innym wypadku,
            proszę powiedzieć koniec.""", "dodatkowe_informacje", [cancel]),
        ("""Dziękuję, powtórzę wszystkie informacje, które zrozumiałam.
            Cel zapisu. {zapis}.
            Nowy klient. {nowy_klient}.
            Imię i nazwisko. {imie_nazwisko}.
            Numer telefonu. {numer_telefonu}
            Numer rejestracyjny samochodu. {numer_rejestracyjny}
            Marka samochodu. {marka}
            Model samochodu. {model}
            Rok produkcji samochodu. {rok_produkcji}
            Dodatkowe informacje. {dodatkowe_informacje}
            Czy wszystko się zgadza?""", "", [cancel]),
        ("""Dziękuję. Zostali Państwo wstępnie zapisani na przegląd. Po zakończeniu rozmowy
            napiszę do Państwa konsultant z potwierdzeniem wizyty. Czy mogłabym w czymś
            jeszcze pomóc?""", "", []),
        9,
    ],
    "CORRECT": """Oczywiście, proszę powiedzieć powoli co mam poprawić, a następnie
        powtórzę wszystko co zrozumiałam.""",
    "WIADOMOŚĆ": [
        ("""Zrozumiałam, że chcą Państwo zostawić wiadomość konsultantowi. W każdym momencie mogą
            Państwo powiedzieć 'anuluj wiadomość', a w takim wypadku wszystkie zapisane informację
            zostaną usunięte. Wszystkie zapisane informację zostaną podane na końcu i będzie można
            je poprawić, jeżeli źle zrozumiałam Państwa odpowiedzi. Na początku chciałabym poprosić
            Państwa o imię i nazwisko.""", "imie_nazwisko", [cancel]),
        ("Dziękuję. Proszę powiedzieć, jaką wiadomość chcą Państwo zostawić?", "wiadomość", [cancel]),
        ("Dziękuję. Proszę podać swój numer telefonu.", "numer_telefonu", [cancel]),
        ("""Dziękuje, powtórzę wszystkie informację, którę zrozumiałam. Proszę powiedzieć 'koniec'
            jeżeli wszystko się zgadza, lub 'nie zgadza się', jeżeli trzeba coś poprawić.
            Imie i nazwisko. {imie_nazwisko}.
            Wiadomość. {wiadomość}.
            Numer telefonu. {numer_telefonu}""", "", [cancel]),
        ("""Dziękuje. Państwa wiadomość została przekazana konsultantowi. Po zakończeniu rozmowy
            dostaną Państwo smsa z potwierdzeniem wizyty. Czy mogłabym w czymś jeszcze pomóc? Aby
            powtórzyć opcję, proszę powiedzieć 'opcje'.""", "", []),
        3,
    ],
}

FLOWS = {
    "ZAPIS": "zapis",
    "WIADOMOŚĆ": "wiadomość",
}

POSSIBILITIES = """ Select which word from POSSIBILITIES resembles the SPEECH the most, if you think that none of them do, select 'none of the above' option:
POSSIBILITIES: lexus, toyota;
SPEECH: Lexus;
MATCH: lexus;
POSSIBILITIES: RAV4, Corolla, Yaris, Aygo;
SPEECH: Raf cztery;
MATCH: RAV4;
POSSIBILITIES: 2010, 2011, 2012, 2013, 2014, 2015;
SPEECH: dwa tysiące dziesięć;
MATCH: 2010;
POSSIBILITIES: LS400, LS600, SC400, IS300, IS220d;
SPEECH: sc-300;
MATCH: none of the above;
POSSIBILITIES: {possibilities};
SPEECH: {speech};
MATCH:
"""
