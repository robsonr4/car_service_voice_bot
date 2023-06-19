from django.http import HttpRequest
from twilio.twiml.voice_response import VoiceResponse
from django.urls import reverse

def cancel(request: HttpRequest, vr: VoiceResponse):
    flow: str = request.session["CURRENT_FLOW"]
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if set(("anuluj", flow)).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = "CANCEL ZAPIS"
        vr.say(f"Czy na pewno chcą państwo anulować {flow}?", voice="alice", language="pl-PL")
        # request.session["CHAT"].append({"role": "assistant", "content": "Anulowali Państwo zapis na przegląd. Czy mógłabym Państwu jeszcze jakoś pomóc? Aby powtórzyć opcje, proszę powiedzieć 'opcje'."})
        vr.redirect("/gather_answer/", method="POST")

def repeat(request: HttpRequest, vr: VoiceResponse):
    """ Check if the caller wants to repeat the last speech."""

    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if "powtórz" in set(last_speech):
        vr.redirect("/gather_answer/", method="POST")
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


def flow_prompt(request: HttpRequest):
    prompt = """Sklasyfikuj temat rozmowy jako ZAPIS (zapisanie klienta na przegląd, wymianę opon, czy inną czynność), WIADOMOŚĆ (przekazanie wiadomości lub pytania), KONIEC (zakończenie rozmowy), lub INNE (jeżeli nie zrozumiałeś tematu wypowiedzi):
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
KONWERSACJA: Za ile będziesz?
TEMAT: INNE
KONWERSACJA: """
    prompt += request.session["CHAT"][-1]["content"]
    prompt += "\nTEMAT: "
    return prompt












# request.session["CHAT"].append(const.PROMPTS["PRZEGLAD"])
        # answer = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=request.session["CHAT"],
        #     temperature=0.8,
        #     max_tokens=150,
        #     n=1,
        #     stop="\n",
        # )
