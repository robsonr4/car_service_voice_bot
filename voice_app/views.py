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
from . import funcs


openai.api_key = settings.OPENAI_API_KEY

request_validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

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
def gather_answer(request: HttpRequest, st: str = "auto"):
    vr = VoiceResponse()

    if "NO SPEECH" in request.session:
        vr.say(request.session["NO SPEECH"], voice="alice", language="pl-PL")
        del request.session["NO SPEECH"]
    elif "CURRENT_FLOW" in request.session and \
    "CANCEL" != request.session["CURRENT_FLOW"].split(" ")[0] and \
    "TEXT" in request.session:
        vr.say(request.session["TEXT"], voice="alice", language="pl-PL")
    elif "CURRENT_FLOW" in request.session and \
    "CANCEL" == request.session["CURRENT_FLOW"].split(" ")[0]:
        flow = request.session["CURRENT_FLOW"].split(" ")[1]
        vr.say(const.PREPARED_TEXT["CANCEL"].format(flow=flow), voice="alice", language="pl-PL")

    if "REPEAT" in request.session and \
    request.session["REPEAT"]:
        request.session["REPEAT"] = False

    vr.gather(
        speechTimeout=st,
        speechModel='experimental_conversations',
        input='speech',
        action='/transfer_to_flow/',
        language='pl-PL',
    )
    vr.redirect('/transfer_to_flow/', method='POST')

    return HttpResponse(str(vr))

@require_POST
@csrf_exempt
def present_prompts(request: HttpRequest):
    vr = VoiceResponse()
    request.session["TEXT"] = const.PREPARED_TEXT["PRESENT PROMPTS"]
    vr.redirect("/gather_answer/5/", method="POST")
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
            "nowy_klient": False
        }
        request.session["REPEAT"] = False
        request.session["NO SPEECH NUM"] = 0

    vr = VoiceResponse()

    ### CHECK IF SPEECH WAS REGISTERED ###
    if request.POST.get('SpeechResult', '') == "" and \
    request.session["NO SPEECH NUM"] < 3:
        request.session["NO SPEECH NUM"] += 1
        request.session["NO SPEECH"] = "Czy Państwo mogą powtórzyć swoją wypowiedź?"
        vr.redirect("/gather_answer/5/", method="POST")
        return HttpResponse(str(vr))
    elif request.POST.get('SpeechResult', '') == "" and \
    request.session["NO SPEECH NUM"] >= 3:
        request.session["NO SPEECH NUM"] = 0
        vr.say("Przepraszam, ale nie mogę Państwa usłyszeć. Proszę zadzwonić ponownie później.", voice="alice", language="pl-PL")
        vr.hangup()
        return HttpResponse(str(vr))
    else:
        request.session["NO SPEECH NUM"] = 0
    ### ADD SPEECH TO CHAT ###
    request.session["CHAT"].append(
        {"role": "user", "content": request.POST.get('SpeechResult', '')}
    )
    print(request.session["CHAT"][-1]["content"])

    ### CHECK IF USER WANTS TO REPEAT ###
    ans = funcs.repeat(request, vr)
    if ans:
        return HttpResponse(str(vr))

    ### CLASSIFY TOPIC OF CONVERSATION IF START ###
    if request.session["CURRENT_FLOW"] == "START":
        request.session["CURRENT_FLOW"] = openai.Completion.create(
            engine="text-davinci-003",
            prompt=funcs.flow_prompt(request),
            temperature=0.2,
            stop="\n",
            max_tokens=150,
            n=1,
        ).choices[0].text.strip() # type: ignore
        request.session["CHAT"].insert(0, const.PROMPTS["GENERAL"])
        request.session["CURRENT_FLOW_NUM"] = 0

    ### CANCLE FLOW ###
    if "CANCEL" in request.session["CURRENT_FLOW"].split(" ")[0] and \
    set(("tak",)).issubset(set(request.session["CHAT"][-1]["content"].lower().split(" "))):
        fl = request.session["CURRENT_FLOW"].split(" ")[1].lower()
        request.session["CURRENT_FLOW"] = "START"
        request.session["CURRENT_FLOW_NUM"] = 0
        del request.session["TEXT"]
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
            "nowy_klient": False
        }
        request.session["REPEAT"] = False
        vr.say(f"{fl} został anulowany, a wraz z nim wszystkie dane.", voice="alice", language="pl-PL")
        vr.redirect("/present_prompts/", method="POST")
        return HttpResponse(str(vr))
    elif "CANCEL" in request.session["CURRENT_FLOW"].split(" ")[0] and \
    set(("nie",)).issubset(set(request.session["CHAT"][-1]["content"].lower().split(" "))):
        print("here nie")
        request.session['CURRENT_FLOW'] = request.session['CURRENT_FLOW'].split(" ")[1]
        vr.say("Anulacja zapisu została odwołana. Powtórzę moją ostatnią wypowiedź.", voice="alice", language="pl-PL")
        request.session["NOT CANCEL"] = True

    print("here")
    print(dict(request.session))
    ### FLOWS ###
    if request.session["CURRENT_FLOW"] == "ZAPIS":

        ### SAVE ANSWER ###
        if "NOT CANCEL" in request.session:
            del request.session["NOT CANCEL"]
        elif request.session["CURRENT_FLOW_NUM"] != 0:
            funcs.save_flow(
                request,
                request.session["CURRENT_FLOW"],
                const.PREPARED_TEXT
            )

        ### ADD TEXT TO BE SAID ###
        if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["ZAPIS"][-1]:
            request.session["TEXT"] = const.PREPARED_TEXT["ZAPIS"][
                request.session["CURRENT_FLOW_NUM"]
            ][0].format(**request.session["CLIENT_DATA"])
            print(request.session["TEXT"])
        else:
            request.session["TEXT"] = const.PREPARED_TEXT["ZAPIS"][
                request.session["CURRENT_FLOW_NUM"]
            ][0]

        ### CHECK IF THIS IS THE END ###
        if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["ZAPIS"][-1] + 1:
            request.session["CURRENT_FLOW"] = "START"
            request.session["CURRENT_FLOW_NUM"] = 0



        # # to chyba do wywalenia
        # if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["ZAPIS"][-2] and \
        # "koniec" in request.session["CHAT"][-1]["content"].lower().split(" "):
        #     ### CHECK IF THIS IS THE END OF FLOW ###
        #     request.session["CURRENT_FLOW"] = "START"
        #     request.session["CURRENT_FLOW_NUM"] = 0

        ### GO THROUGH ALL FUNCS ###
        for func in const.PREPARED_TEXT["ZAPIS"][request.session["CURRENT_FLOW_NUM"]][2]:
            ans = func(request, vr)
            if ans:
                return HttpResponse(str(vr))
        print("here again")

        request.session["CURRENT_FLOW_NUM"] += 1
        vr.redirect("/gather_answer/", method="POST")

    elif request.session["CURRENT_FLOW"] == "KONIEC":
        vr.say("Dziękuję za rozmowę. Miłego dnia.", voice="alice", language="pl-PL")
        vr.hangup()
        return HttpResponse(str(vr))

    # vr.say(answer.choices[0].message["content"], voice="alice", language="pl-PL") # type: ignore
    # request.session["CHAT"].append({"role": "assistant", "content": answer.choices[0].message["content"]}) # type: ignore
    print(request.session["CHAT"])
    print(request.session["CLIENT_DATA"])
    return HttpResponse(str(vr))
