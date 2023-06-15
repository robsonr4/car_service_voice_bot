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
    "PRESENT PROMPTS": """Możesz mnie poprosić o zapisanie na jedną lub więcej z oferowanych przez nas usług, lub o przekazanie wiadomości/pytania dla konsultanta. Aby powtórzyć opcje, proszę powiedzieć 'opcje'. Jak mogę pomóc?""",
    "GREET CLIENT": """Cześć, to jest automatyczna sekretarka serwisu Lexusa, Toyoty. W czym mógłabym Państwu dzisiaj pomóc?""",
    "ZAPIS": [
        ("Na jaką usługę/usługi chcieliby Państwo się zapisać?", "zapis", [funcs.cancel]),
        ("Dziękuję. Chciałabym się zapytać, czy Państwo już byli u nas w serwisie?", "nowy_klient", [funcs.cancel]),
        ("Dziękuję. Poprosiłabym Państwa o imię i nazwisko.", "imie_nazwisko", [funcs.cancel]),
        ("Dziękuję. Proszę podać swój numer telefonu.", "numer_telefonu", [funcs.cancel]),
        ("Dziękuję. Proszę powoli przeliterować numer rejestracyjny samochodu.", "numer_rejestracyjny", [funcs.cancel]),
        ("Dziękuję. Prosze podać markę samochodu.", "marka", [funcs.cancel]),
        ("Dziękuję. Proszę podać model samochodu.", "model", [funcs.cancel]),
        ("Dziękuję. Proszę podać rok produkcji samochodu.", "rok_produkcji", [funcs.cancel]),
        ("Dziękuję. Proszę podać dodatkowe informacje, jeżeli takie są. W innym wypadku, proszę powiedzieć koniec.", "dodatkowe_informacje", [funcs.cancel, funcs.end]),
        ("""Dziękuje, powtórzę wszystkie informację, którę zrozumiałam. Proszę powiedzieć 'koniec' jeżeli wszystko się zgadza, lub 'nie zgadza się', jeżeli trzeba coś poprawić.
        Cel zapisu: {zapis}
        Imię i nazwisko: {imie_nazwisko}
        Numer telefonu: {numer_telefonu}
        Numer rejestracyjny samochodu: {numer_rejestracyjny}
        Marka samochodu: {marka}
        Model samochodu: {model}
        Rok produkcji samochodu: {rok_produkcji}
        Dodatkowe informacje: {dodatkowe_informacje}""", "", [funcs.cancel, funcs.repeat]),
        ("Dziękuje. Państwo zostali zapisani na przegląd. Po zakończeniu rozmowy dostaną państwo smsa z potwierdzeniem wizity. Czy mógłbym w czymś jeszcze pomóc?", "zapis", [funcs.cancel, funcs.end]),
        6,
        9,
        ("Oczywiście, proszę powiedzieć co mam poprawić, a następnie powtórzę wszystko co zrozumiałam.", "", [funcs.cancel]),
    ],
    "WIADOMOŚĆ": []
}

FLOWS = {
    "ZAPIS": "zapis",
    "WIADOMOŚĆ": "wiadomość",
}