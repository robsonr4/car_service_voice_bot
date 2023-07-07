from django.http import HttpRequest
from twilio.twiml.voice_response import VoiceResponse
from django.urls import reverse
import openai
from django.conf import settings
from .models import Car

openai.api_key = settings.OPENAI_API_KEY


def cancel(request: HttpRequest, vr: VoiceResponse):
    """ Check if the caller wants to cancel the current flow."""

    flow: str = request.session["CURRENT_FLOW"].lower()
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if set(("anuluj", flow)).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = f"CANCEL {flow}"
        request.session["CURRENT_FLOW_NUM"] -= 1
        # request.session["CHAT"].append({"role": "assistant", "content": "Anulowali Państwo zapis na przegląd. Czy mógłabym Państwu jeszcze jakoś pomóc? Aby powtórzyć opcje, proszę powiedzieć 'opcje'."})
        vr.redirect("/gather_answer/", method="POST")
        return True

def repeat(request: HttpRequest, vr: VoiceResponse):
    """ Check if the caller wants to repeat the last speech."""

    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if "powtórz" in set(last_speech):
        request.session["REPEAT"] = True
        vr.redirect("/gather_answer/", method="POST")
        return True
    else:
        return False

def end(request: HttpRequest, vr: VoiceResponse):
    """ Chech if the caller wants to end the conversation."""

    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if "koniec" in set(last_speech):
        vr.redirect(reverse("gather_answer"), method="POST")
    else:
        return False

def correct(request: HttpRequest, vr: VoiceResponse):
    """ Check if the caller wants to correct the saved information,
and if yes, then gather the answer and correct info in correct_message func."""
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    flow = request.session["CURRENT_FLOW"]
    if set(("tak", )).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = f"CORRECT {flow}"
        request.session["TEXT"] = CORRECT
        request.session["CURRENT_FLOW_NUM"] -= 1
        vr.redirect("/gather_answer/", method="POST")
        return True
    else:
        return False
    
    
def correct_message(request: HttpRequest):
    """ Correct the client's data."""
    flow = request.session["CURRENT_FLOW"].split(" ")[1]
    if flow == "ZAPIS":
        fields = [
            "zapis", "nowy_klient", "imie_nazwisko", 
            "numer_telefonu", "numer_rejestracyjny", 
            "marka", "model", "rok_produkcji", 
            "dodatkowe_informacje"
        ]
    else:
        fields = [
            "imie_nazwisko", "wiadomość",
            "numer_telefonu", 
        ]
    cl = ""
    for field in fields:
        cl += f" | {field}: {request.session['CLIENT_DATA'][field]}"
    answer = request.session["CHAT"][-1]["content"]
    prompt = CORRECT_MESSAGE.format(
        client_data=cl,
        speech=answer)
    
    ans = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.2,
            stop="\n",
            max_tokens=400,
        )
    matched_ans = ans.choices[0].text.strip().split(' | ')[1:]

    for i, field in enumerate(fields):
        request.session["CLIENT_DATA"][field] = matched_ans[i].split(":")[1].strip()


    request.session["CURRENT_FLOW"] = flow

def save_flow(request: HttpRequest, flow: str, PREPARED_TEXT: dict, vr: VoiceResponse):
    """ Save the client's data."""

    bool_vars = ["nowy_klient"]
    str_vars = [
        "zapis", "imie_nazwisko", "numer_rejestracyjny", "dodatkowe_informacje",
        "numer_telefonu", "wiadomość"
    ]
    spec_vars = ["marka", "model", "rok_produkcji"]
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    var_name = PREPARED_TEXT[flow][request.session["CURRENT_FLOW_NUM"] - 1][1]

    if var_name in bool_vars and \
    set(("tak", )).issubset(set(last_speech)):
        request.session["CLIENT_DATA"][var_name] = "Nie"
        return True
    elif var_name in bool_vars and \
    set(("nie", )).issubset(set(last_speech)):
        request.session["CLIENT_DATA"][var_name] = "Tak"
        return True
    elif var_name in str_vars:
        ans = request.session["CHAT"][-1]["content"].strip()
        if "numer_telefonu" in var_name:
            request.session["CLIENT_DATA"][var_name] = " ".join(ans)
        else:
            request.session["CLIENT_DATA"][var_name] = ans
        return True
    elif var_name in spec_vars:
        if request.session["CLIENT_DATA"]["marka"] == "":
            ans = check_with_db(request.session["CHAT"][-1]["content"], "marka", {})
            if ans.lower() != "again":
                request.session["CLIENT_DATA"][var_name] = ans.lower()
                request.session["INCORRECT_CAR"] = 0
            elif request.session["INCORRECT_CAR"] < 2:
                request.session["TEXT"] = NOT_MARKA.format(
                    marka=request.session["CHAT"][-1]["content"]
                )
                vr.redirect("/gather_answer/5/", method="POST")
                request.session["INCORRECT_CAR"] += 1
                return False
            else:
                vr.say(
                    NOT_3_MARKA.format(
                        marka=request.session["CHAT"][-1]["content"],
                    ), 
                    voice="alice", 
                    language="pl-PL"
                )
                vr.hangup()
                return False
        elif request.session["CLIENT_DATA"]["model"] == "":
            filt = {"marka": request.session["CLIENT_DATA"]["marka"]}
            ans = check_with_db(request.session["CHAT"][-1]["content"], "model", filt)
            if ans.lower() != "again":
                request.session["CLIENT_DATA"][var_name] = ans
                request.session["INCORRECT_CAR"] = 0
            elif request.session["INCORRECT_CAR"] < 2:
                request.session["TEXT"] = NOT_MODEL.format(
                    marka=request.session["CLIENT_DATA"]["marka"],
                    model=request.session["CHAT"][-1]["content"]
                )
                vr.redirect("/gather_answer/5/", method="POST")
                request.session["INCORRECT_CAR"] += 1
                return False
            else:
                vr.say(
                    NOT_3_MODEL.format(
                        marka=request.session["CLIENT_DATA"]["marka"],
                        model=request.session["CHAT"][-1]["content"],
                    ), 
                    voice="alice", 
                    language="pl-PL"
                )
                vr.hangup()
                return False
        else:
            filt = {"marka": request.session["CLIENT_DATA"]["marka"], "model": request.session["CLIENT_DATA"]["model"]}
            ans = check_with_db(request.session["CHAT"][-1]["content"], "rok_produkcji", filt)
            if ans.lower() != "again":
                request.session["CLIENT_DATA"][var_name] = ans
                request.session["INCORRECT_CAR"] = 0
            elif request.session["INCORRECT_CAR"] < 2:
                request.session["TEXT"] = NOT_ROK.format(
                    marka=request.session["CLIENT_DATA"]["marka"],
                    model=request.session["CLIENT_DATA"]["model"],
                    rok_produkcji=request.session["CHAT"][-1]["content"],
                )
                vr.redirect("/gather_answer/5/", method="POST")
                request.session["INCORRECT_CAR"] += 1
                return False
            else:
                vr.say(
                    NOT_3_ROK.format(
                        marka=request.session["CLIENT_DATA"]["marka"],
                        model=request.session["CLIENT_DATA"]["model"],
                        rok_produkcji=request.session["CHAT"][-1]["content"],
                    ), 
                    voice="alice", 
                    language="pl-PL"
                )
                vr.hangup()
                return False
        return True


    return request.session["CLIENT_DATA"]


def check_with_db(answer, possible_answers, filt):
    """ Check if the answer is in the database. """
    possible_answers = Car.objects.filter(**filt).values_list(possible_answers, flat=True).distinct()
    possible_answers = [str(x) for x in possible_answers]
    prompt = POSSIBILITIES.format(
        possibilities=", ".join(possible_answers),
        speech=answer)
        
    ans = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.2,
            stop="\n",
            max_tokens=150,
        )
    matched_ans = ans.choices[0].text.strip()

    return matched_ans
    

def flow_prompt(request: HttpRequest):
    prompt = """Sklasyfikuj temat rozmowy jako ZAPIS (zapisanie klienta na przegląd, wymianę opon, czy inną czynność), WIADOMOŚĆ (przekazanie wiadomości lub pytania), KONIEC (zakończenie rozmowy), OPCJE (powtórz opcje dla klienta) lub INNE (jeżeli nie zrozumiałeś tematu wypowiedzi):
KONWERSACJA: Dzień dobry, mam pytanie na temat ceny przeglądu samochodu. Ile kosztuje przegląd samochodu?
TEMAT: WIADOMOŚĆ
KONWERSACJA: Chciałbym zostawić wiadomość Pani Paulinie
TEMAT: WIADOMOŚĆ
KONWERSACJA: Chciałbym zapisać się na sprawdzenie czeków w samochodzie
TEMAT: ZAPIS
KONWERSACJA: Dzień dobry, chciałbym zapytać o wymianę opon
TEMAT: WIADOMOŚĆ
KONWERSACJA: Przekaż informację Panu Jerzemu
TEMAT: WIADOMOŚĆ
KONWERSACJA: Chciałbym się skontaktować w sprawie naprawy samochodu
TEMAT: WIADOMOŚĆ
KONWERSACJA: Zapis na przegląd samochodu
TEMAT: ZAPIS
KONWERSACJA: To wszystko, dziękuję
TEMAT: KONIEC
KONWERSACJA: Odpowiedz na pytanie na jakiś temat
TEMAT: WIADOMOŚĆ
KONWERSACJA: Chcę wymienić wycieraczki
TEMAT: ZAPIS
KONWERSACJA: Powtórz opcję do wyboru
TEMAT: OPCJE
KONWERSACJA: O co mógłbym poprosić?
TEMAT: OPCJE
KONWERSACJA: koniec
TEMAT: KONIEC
KONWERSACJA: Za ile będziesz?
TEMAT: INNE
KONWERSACJA: nie
TEMAT: KONIEC
KONWERSACJA: Chciałbym się zapytać czy mógłbym przy okazji zostawienia mojego lexusa odebrać rx400, który jest u Państwa na serwisie?
TEMAT: WIADOMOŚĆ
KONWERSACJA: """

    prompt += request.session["CHAT"][-1]["content"]
    prompt += "\nTEMAT: "
    return prompt


CORRECT_MESSAGE = """ Dane, które są podane, są niepoprawne. Bazując na tym, co powiedział klient, popraw dane, które są niepoprawne:
CLIENT_DATA: | zapis: Wymiana świec | nowy_klient: False | imie_nazwisko: Paweł Pawlak | numer_telefonu: 1 2 3 1 2 3 1 2 3 | numer_rejestracyjny: WB44444 | marka: toyota | model: Auris | rok_produkcji: 2014 | dodatkowe_informacje: koniec;
SPEECH: Moję imię to Paweł Pawluk, nie Paweł Pawlak, oraz mój numer rejestracyjny to WB44443;
NEW_CLIENT_DATA: | zapis: Wymiana świec | nowy_klient: False | imie_nazwisko: Paweł Pawluk | numer_telefonu: 1 2 3 1 2 3 1 2 3 | numer_rejestracyjny: WB44443 | marka: toyota | model: Auris | rok_produkcji: 2014 | dodatkowe_informacje: koniec
CLIENT_DATA: | zapis: Wymiana świec | nowy_klient: False | imie_nazwisko: Paweł Pawlak | numer_telefonu: 1 2 3 1 2 3 1 2 3 | numer_rejestracyjny: WB44444 | marka: toyota | model: Auris | rok_produkcji: 2014 | dodatkowe_informacje: Auto jest po wypadku, proszę o delikatne podejście;
SPEECH: Moję imię to Paweł Pawluk, nie Paweł Pawlak, oraz mój numer rejestracyjny to WB44443;
NEW_CLIENT_DATA: | zapis: Wymiana świec | nowy_klient: False | imie_nazwisko: Paweł Pawluk | numer_telefonu: 1 2 3 1 2 3 1 2 3 | numer_rejestracyjny: WB44443 | marka: toyota | model: Auris | rok_produkcji: 2014 | dodatkowe_informacje: Auto jest po wypadku, proszę o delikatne podejście
CLIENT_DATA: | imie_nazwisko: Ania Enty | wiadomość: Ile zajmie wymiana świec w lexusie rx 400? | numer_telefonu: 3 3 4 3 3 4 3 3 4;
SPEECH: Jest błąd w numerze telefonu, mój numer telefonu to 3 3 4 3 3 4 3 3 5;
NEW_CLIENT_DATA: | imie_nazwisko: Ania Enty | wiadomość: Ile zajmie wymiana świec w lexusie rx 400? | numer_telefonu: 3 3 4 3 3 4 3 3 5
CLIENT_DATA: {client_data};
SPEECH: {speech};
"""

CORRECT = """Oczywiście, proszę powiedzieć powoli co mam poprawić, a następnie
        powtórzę wszystko co zrozumiałam."""

POSSIBILITIES = """ Select which word from POSSIBILITIES resembles the SPEECH the most, if you think that none of them do or there is more than 1 possibility, write 'again':
POSSIBILITIES: lexus, toyota;
SPEECH: Lexus;
MATCH: Lexus
POSSIBILITIES: RAV4, Corolla, Yaris, Aygo;
SPEECH: Raf cztery;
MATCH: RAV4
POSSIBILITIES: 2010, 2011, 2012, 2013, 2014, 2015;
SPEECH: dwa tysiące dziesięć;
MATCH: 2010
POSSIBILITIES: LS400, LS600, SC400, IS300, IS220d;
SPEECH: sc-300;
MATCH: again
POSSIBILITIES: RAV4, Corolla, Yaris, Aygo;
SPEECH: Aygo;
MATCH: Aygo
POSSIBILITIES: {possibilities};
SPEECH: {speech};
MATCH: """

NOT_MARKA = """Przepraszam ale podana marka -  {marka} - nie istnieje w naszej bazie, lub nie jest
               obsługiwana przez nasz serwis. Czy mogłabym Państwa poprosić o powtórzenie odpowiedzi?"""

NOT_3_MARKA = """Przepraszam ale podana marka - {marka} - nie istnieje w naszej bazie, lub nie jest
                 obsługiwana przez nasz serwis. Przez ilość powtórzeń rozmowa zostanie zakończona.
                 W razie potrzeby, proszę zostawić wiadomość. Życzę miłego dnia."""

NOT_MODEL = """Przepraszam ale podany model -  {model} - dla marki {marka} nie istnieje w naszej bazie.
               Czy mogłabym Państwa poprosić o powtórzenie odpowiedzi?"""

NOT_3_MODEL = """Przepraszam ale podany model -  {model} - dla marki {marka} nie istnieje w naszej bazie.
                 Zostaną Państwo przekazani konsultantowi naszego serwisu, proszę czekać."""

NOT_ROK = """Przepraszam ale podany rok produkcji-  {rok_produkcji} - dla marki {marka} i modelu {model}
             nie istnieje w naszej bazie. Czy mogłabym Państwa poprosić o powtórzenie odpowiedzi?"""

NOT_3_ROK = """Przepraszam ale podany rok produkcji- {rok_produkcji} - dla marki {marka} i modelu {model}
               nie istnieje w naszej bazie. Zostaną Państwo przekazani konsultantowi naszego serwisu, proszę czekać."""
