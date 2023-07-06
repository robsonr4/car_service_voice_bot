from django.http import HttpRequest
from twilio.twiml.voice_response import VoiceResponse
from django.urls import reverse
import openai
from django.conf import settings
from .models import Car

openai.api_key = settings.OPENAI_API_KEY


def cancel(request: HttpRequest, vr: VoiceResponse):
    flow: str = request.session["CURRENT_FLOW"].lower()
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if set(("anuluj", flow)).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = "CANCEL ZAPIS"
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

def fix_zapis(request: HttpRequest, vr: VoiceResponse):
    """ Check if the caller wants to correct the saved information,
and if yes, then gather the answer and correct info."""

    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if set(("nie", "zgadza")).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = "POPRAWA ZAPIS"
        vr.say(
            "Oczywiście, proszę powiedzieć powoli co mam poprawić, a następnie powtórzę wszystko co zrozumiałam.",
            voice="alice",
            language="pl-PL")
        vr.redirect("/gather_answer/", method="POST")
    else:
        return False

def save_flow(request: HttpRequest, flow: str, PREPARED_TEXT: dict):
    """ Save the client's data in the zapis flow."""

    bool_vars = ["nowy_klient"]
    str_vars = [
        "zapis", "imie_nazwisko", "numer_rejestracyjny", "dodatkowe informacje",
        "numer_telefonu", "wiadomość"
    ]
    spec_vars = ["marka", "model", "rok_produkcji"]
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    var_name = PREPARED_TEXT[flow][request.session["CURRENT_FLOW_NUM"] - 1][1]

    if var_name in bool_vars and \
    set(("tak", )).issubset(set(last_speech)):
        request.session["CLIENT_DATA"][var_name] = False
        return True
    elif var_name in bool_vars and \
    set(("nie", )).issubset(set(last_speech)):
        request.session["CLIENT_DATA"][var_name] = True
        return True
    elif var_name in str_vars:
        request.session["CLIENT_DATA"][var_name] = request.session["CHAT"][-1]["content"].strip()
        return True
    elif var_name in spec_vars:
        if request.session["CLIENT_DATA"]["marka"] == "":
            ans = check_with_db(request.session["CHAT"][-1]["content"], "marka", {})
            request.session["CLIENT_DATA"][var_name] = ans.lower()
        elif request.session["CLIENT_DATA"]["model"] == "":
            filt = {"marka": request.session["CLIENT_DATA"]["marka"]}
            ans = check_with_db(request.session["CHAT"][-1]["content"], "model", filt)
            request.session["CLIENT_DATA"][var_name] = ans
        else:
            filt = {"marka": request.session["CLIENT_DATA"]["marka"], "model": request.session["CLIENT_DATA"]["model"]}
            ans = check_with_db(request.session["CHAT"][-1]["content"], "rok_produkcji", filt)
            request.session["CLIENT_DATA"][var_name] = ans
        return True


    return request.session["CLIENT_DATA"]

def check_with_db(answer, possible_answers, filt):
    possible_answers = Car.objects.filter(**filt).values_list(possible_answers, flat=True).distinct()
    possible_answers = [str(x) for x in possible_answers]
    prompt = POSSIBILITIES.format(
        possibilities=", ".join(possible_answers),
        speech=answer)
    print(prompt)
    ans = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.2,
            stop="\n",
            max_tokens=150,
        )
    matched_ans = ans.choices[0].text.strip()
    print(matched_ans)

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
KONWERSACJA: Chciałbym się zapytać czy mógłbym przy okazji zostawienia mojego lexusa odebrać rx400, który jest u Państwa na serwisie?
TEMAT: WIADOMOŚĆ
KONWERSACJA: """

    prompt += request.session["CHAT"][-1]["content"]
    prompt += "\nTEMAT: "
    return prompt





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

# request.session["CHAT"].append(const.PROMPTS["PRZEGLAD"])
        # answer = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=request.session["CHAT"],
        #     temperature=0.8,
        #     max_tokens=150,
        #     n=1,
        #     stop="\n",
        # )
