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
    "PRZEGLĄD": [
        ("{pr}. Jeżeli Państwo mieli inny cel zapisu, na końcu będzie możliwość zmienienia celu. Jeżeli państwo nie chcieli się zapisać na żadną z usług, proszę powiedzieć 'anuluj zapis'. W innym razie, proszę podać swoje imię i nazwisko.", "imie_nazwisko", ["anuluj zapis"]),
        ("Dziękuję. Proszę podać swój numer telefonu.", "numer_telefonu", ["anuluj zapis"]),
        "Dziękuję. Proszę powoli przeliterować numer rejestracyjny samochodu.",
        "Dziękuję. Prosze podać markę samochodu."
        "Dziękuję. Proszę podać model samochodu.",
        "Dziękuję. Proszę podać rok produkcji samochodu.",
        "Dziękuję. Proszę podać dodatkowe informacje, jeżeli takie są. W innym wypadku, proszę powiedzieć koniec.",
        "Zapisałem dodatkowe informację, jeżeli mają państwo jeszcze jakieś dodatkowe informacje, proszę powiedzieć. W innym wypadku, proszę powiedzieć koniec.",
        """Dziękuje, powtórzę zapisane informację. Proszę powiedzieć 'zgadza się' jeżeli wszystko się zgadza, lub 'nie zgadza się' jeżeli trzeba coś poprawić.
        Cel zapisu: {zapis}
        Imię i nazwisko: {imie_nazwisko}
        Numer telefonu: {numer_telefonu}
        Numer rejestracyjny samochodu: {numer_rejestracyjny}
        Marka samochodu: {marka}
        Model samochodu: {model}
        Rok produkcji samochodu: {rok_produkcji}
        Dodatkowe informacje: {dodatkowe_informacje}"""
        "Dziękuje. Państwo zostali zapisani na przegląd. Po zakończeniu rozmowy dostaną państwo smsa z potwierdzeniem wizity. Czy mógłbym w czymś jeszcze pomóc?",
        6,
        9
    ]
}

FLOWS = {
    "ZAPIS": "zapis",
    "WIADOMOŚĆ": "wiadomość",
}