from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import SuspiciousOperation
from twilio.request_validator import RequestValidator
from django.http import HttpRequest, HttpResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.http import Response
from django.urls import reverse
import openai
from . import const
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

@require_POST
@csrf_exempt
def greet_client(request: HttpRequest):
    """ Greet the caller and tranfer them to particular conversation flow.
    """
    vr = VoiceResponse()
    vr.say(const.PREPARED_TEXT["GREET CLIENT"], voice="alice", language="pl-PL", )
    vr.redirect(reverse("present_prompts"), method="POST")
    return HttpResponse(str(vr))


@require_POST
@csrf_exempt
def gather_answer(request: HttpRequest):
    vr = VoiceResponse()
    if "CANCEL" != request.session["CURRENT_FLOW"] and \
    "TEXT" in request.session:
        vr.say(request.session["TEXT"], voice="alice", language="pl-PL")
        del request.session["TEXT"]
    vr.gather(
        speechTimeout="auto",
        speechModel='experimental_conversations',
        input='speech',
        action='/transfer_to_flow/',
        language='pl-PL',
    )
    return HttpResponse(str(vr))

@require_POST
@csrf_exempt
def present_prompts(request: HttpRequest):
    vr = VoiceResponse()
    vr.say(const.PREPARED_TEXT["PRESENT PROMPTS"], voice="alice", language="pl-PL")
    vr.redirect(reverse("gather_answer"), method="POST")
    return HttpResponse(str(vr))

@require_POST
@csrf_exempt
def transfer_to_flow(request: HttpRequest):
    """ Transfer the caller to particular conversation flow.
    """
    ### ADD ALL VARIABLES TO SESSION ###
    if "CHAT" not in request.session or \
    "CURRENT_FLOW" not in request.session or \
    "CLIENT_DATA" not in request.session or \
    "CURRENT_FLOW_NUM" not in request.session:
        request.session["CHAT"] = []
        request.session["CHAT"].append(
            {"role": "assistant", "content": const.PREPARED_TEXT["GREET CLIENT"]}
        )
        request.session["CHAT"].append(
            {"role": "assistant", "content": const.PREPARED_TEXT["PRESENT PROMPTS"]}
        )
        request.session["CURRENT_FLOW"] = "START"
        request.session["CURRENT_FLOW_NUM"] = 0
        request.session["CLIENT_DATA"] = {
            "zapis_done": False,
            "zapis": "",
            "imie_nazwisko": "",
            "numer_telefonu": "",
            "numer_rejestracyjny": "",
            "marka": "",
            "model": "",
            "rok_produkcji": "",
            "dodatkowe_informacje": "",
            "wiadomość_done": False,
            "wiadomość": "",
            "pytanie_done": False,
            "pytanie": "",
        }

    ### ADD SPEECH TO CHAT ###
    request.session["CHAT"].append(
        {"role": "user", "content": request.POST.get('SpeechResult', '')}
    )

    ### CLASSIFY TOPIC OF CONVERSATION IF START ###
    if request.session["CURRENT_FLOW"] == "START":
        request.session["CURRENT_FLOW"] = openai.Completion.create(
            engine="davinci",
            prompt=flow_prompt(request),
            temperature=0.3,
            stop="\n",
            max_tokens=150,
            n=1,
        ).choices[0].text.strip()
        print(request.session["CURRENT_FLOW"])
        request.session["CHAT"].insert(0, const.PROMPTS["GENERAL"])
        request.session["CURRENT_FLOW_NUM"] = 0

    vr = VoiceResponse()

    ### FLOWS ###
    if request.session["CURRENT_FLOW"] == "ZAPIS":
        request.session["TEXT"] = const.PREPARED_TEXT["PRZEGLĄD"][
            request.session["CURRENT_FLOW_NUM"]
        ]

        if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["PRZEGLĄD"][-1]:
            ### CHECK IF THIS IS THE END OF FLOW ###
            request.session["CURRENT_FLOW"] = "START"
            request.session["CURRENT_FLOW_NUM"] = 0

        # to chyba do wywalenia
        if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["PRZEGLĄD"][-2] and \
        "koniec" in request.session["CHAT"][-1]["content"].lower().split(" "):
            ### CHECK IF THIS IS THE END OF FLOW ###
            request.session["CURRENT_FLOW"] = "START"
            request.session["CURRENT_FLOW_NUM"] = 0

        request.session["CURRENT_FLOW_NUM"] += 1
        print(request.session["CHAT"])
        vr.redirect(reverse("gather_answer"), method="POST")



    # vr.say(answer.choices[0].message["content"], voice="alice", language="pl-PL") # type: ignore
    # request.session["CHAT"].append({"role": "assistant", "content": answer.choices[0].message["content"]}) # type: ignore
    print(request.session["CHAT"])
    return HttpResponse(str(vr))


def cancel(request: HttpRequest, vr: VoiceResponse):
    flow = request.session["CURRENT_FLOW"]
    last_speech = request.session["CHAT"][-1]["content"].lower().split(" ")
    if set(("anuluj", flow)).issubset(set(last_speech)):
        request.session["CURRENT_FLOW"] = "CANCEL"
        request.session["CURRENT_FLOW_NUM"] = 0
        vr.say(f"Czy na pewno chcą państwo anulować {flow}?", voice="alice", language="pl-PL")
        request.session["CHAT"].append({"role": "assistant", "content": "Anulowali Państwo zapis na przegląd. Czy mógłabym Państwu jeszcze jakoś pomóc? Aby powtórzyć opcje, proszę powiedzieć 'opcje'."})
        vr.redirect(reverse("gather_answer"), method="POST")



def flow_prompt(request):
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