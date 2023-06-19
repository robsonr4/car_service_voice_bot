from . import funcs

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
    "PRESENT PROMPTS": "Możesz mnie poprosić o zapisanie na jedną lub więcej z oferowanych przez nas usług, lub o przekazanie wiadomości/pytania dla konsultanta. Aby powtórzyć moją ostatnią wypowiedź w jakimkolwiek momencie rozmowy, proszę powiedzieć 'powtórz'. Jak mogę pomóc?",
    "GREET CLIENT": "Cześć, to jest automatyczna sekretarka serwisu Lexusa, Toyoty. W czym mógłabym Państwu dzisiaj pomóc?",
    "ZAPIS": [
        ("Zrozumiałam, że chcą Państwo się zapisać na serwis. W każdym momencie mogą Państwo powiedzieć 'anuluj zapis', a w takim wypadku wszystkie zapisane informację zostaną usunięte. Wszystkie zapisane informację zostaną podane na końcu i będzie można je poprawić, jeżeli źle zrozumiała Państwa odpowiedzi. Na początku chciałabym się zapytać, na jaką usługę/usługi chcieliby Państwo się zapisać?", "zapis", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Chciałabym się zapytać, czy Państwo już byli u nas w serwisie? Proszę odpowiedzieć 'tak' lub 'nie'.", "nowy_klient", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Poprosiłabym Państwa o imię i nazwisko.", "imie_nazwisko", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Proszę podać swój numer telefonu.", "numer_telefonu", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Proszę powoli przeliterować numer rejestracyjny samochodu.", "numer_rejestracyjny", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Prosze podać markę samochodu.", "marka", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Proszę podać model samochodu.", "model", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Proszę podać rok produkcji samochodu.", "rok_produkcji", [funcs.cancel, funcs.repeat]),
        ("Dziękuję. Proszę podać dodatkowe informacje, jeżeli takie są. W innym wypadku, proszę powiedzieć koniec.", "dodatkowe_informacje", [funcs.cancel, funcs.repeat]),
        ("""Dziękuje, powtórzę wszystkie informację, którę zrozumiałam. Proszę powiedzieć 'koniec' jeżeli wszystko się zgadza, lub 'nie zgadza się', jeżeli trzeba coś poprawić.
        Cel zapisu: {zapis}
        Imię i nazwisko: {imie_nazwisko}
        Numer telefonu: {numer_telefonu}
        Numer rejestracyjny samochodu: {numer_rejestracyjny}
        Marka samochodu: {marka}
        Model samochodu: {model}
        Rok produkcji samochodu: {rok_produkcji}
        Dodatkowe informacje: {dodatkowe_informacje}""", "", [funcs.cancel, funcs.repeat, funcs.end]),
        ("Dziękuje. Państwo zostali zapisani na przegląd. Po zakończeniu rozmowy dostaną państwo smsa z potwierdzeniem wizity. Czy mógłbym w czymś jeszcze pomóc?", "", [funcs.repeat]),
        6,
        9,
    ],
    "POPRAWA ZAPISU": [
        ("""Dziękuje, powtórzę wszystkie informację, którę zrozumiałam. Proszę powiedzieć 'koniec' jeżeli wszystko się zgadza, lub 'nie zgadza się', jeżeli trzeba coś poprawić.
        Cel zapisu: {zapis}
        Imię i nazwisko: {imie_nazwisko}
        Numer telefonu: {numer_telefonu}
        Numer rejestracyjny samochodu: {numer_rejestracyjny}
        Marka samochodu: {marka}
        Model samochodu: {model}
        Rok produkcji samochodu: {rok_produkcji}
        Dodatkowe informacje: {dodatkowe_informacje}""", "", [funcs.cancel, funcs.repeat]),
    ],
    "WIADOMOŚĆ": []
}

FLOWS = {
    "ZAPIS": "zapis",
    "WIADOMOŚĆ": "wiadomość",
}