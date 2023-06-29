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

    if "CURRENT_FLOW" in request.session and \
    "CANCEL" != " ".split(request.session["CURRENT_FLOW"])[0] and \
    "TEXT" in request.session:
        vr.say(request.session["TEXT"], voice="alice", language="pl-PL")
        del request.session["TEXT"]

    if "REPEAT" in request.session and \
    request.session["REPEAT"]:
        del request.session["REPEAT"]

    vr.gather(
        speechTimeout=st,
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

    ### ADD SPEECH TO CHAT ###
    request.session["CHAT"].append(
        {"role": "user", "content": request.POST.get('SpeechResult', '')}
    )
    print(request.session["CHAT"][-1]["content"])
    vr = VoiceResponse()

    ### CHECK IF USER WANTS TO REPEAT ###
    funcs.repeat(request, vr)

    ### CLASSIFY TOPIC OF CONVERSATION IF START ###
    if request.session["CURRENT_FLOW"] == "START":
        request.session["CURRENT_FLOW"] = openai.Completion.create(
            engine="davinci",
            prompt=funcs.flow_prompt(request),
            temperature=0.3,
            stop="\n",
            max_tokens=150,
            n=1,
        ).choices[0].text.strip() # type: ignore
        request.session["CHAT"].insert(0, const.PROMPTS["GENERAL"])
        request.session["CURRENT_FLOW_NUM"] = 0

    print("here")
    ### FLOWS ###
    if request.session["CURRENT_FLOW"] == "ZAPIS":

        ### SAVE ANSWER ###
        if request.session["CURRENT_FLOW_NUM"] != 0:
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
            func(request, vr)

        request.session["CURRENT_FLOW_NUM"] += 1
        vr.redirect("/gather_answer/5/", method="POST")



    # vr.say(answer.choices[0].message["content"], voice="alice", language="pl-PL") # type: ignore
    # request.session["CHAT"].append({"role": "assistant", "content": answer.choices[0].message["content"]}) # type: ignore
    print(request.session["CHAT"])
    print(request.session["CLIENT_DATA"])
    return HttpResponse(str(vr))
