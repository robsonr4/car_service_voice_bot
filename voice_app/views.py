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
    if "TEXT" in request.session:
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

    if "CHAT" not in request.session: 
        request.session["CHAT"] = []
        request.session["CHAT"].append({"role": "assistant", "content": const.PREPARED_TEXT["GREET CLIENT"]}) 
        request.session["CHAT"].append({"role": "assistant", "content": const.PREPARED_TEXT["PRESENT PROMPTS"]})
    if "CURRENT_FLOW" not in request.session:
        request.session["CURRENT_FLOW"] = "START"
    request.session["CHAT"].append({"role": "user", "content": request.POST.get('SpeechResult', '')})

    if request.session["CURRENT_FLOW"] == "START":
        request.session["CURRENT_FLOW"] = openai.Completion.create(
            engine="davinci",
            prompt=flow_prompt(request),
            temperature=0.2,
            stop="\n",
            n=1,
        ).choices[0].text.strip()
        print(request.session["CURRENT_FLOW"])
        request.session["CHAT"].insert(0, const.PROMPTS["GENERAL"])
        request.session["CURRENT_FLOW_NUM"] = 0
    vr = VoiceResponse()  
     
    if request.session["CURRENT_FLOW"] == "PRZEGLĄD":
        # request.session["CHAT"].append(const.PROMPTS["PRZEGLAD"])
        # answer = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=request.session["CHAT"], 
        #     temperature=0.8,
        #     max_tokens=150,
        #     n=1,
        #     stop="\n",
        # )
        


        request.session["TEXT"] = const.PREPARED_TEXT["PRZEGLĄD"][request.session["CURRENT_FLOW_NUM"]]
        

        if request.session["CURRENT_FLOW_NUM"] == const.PREPARED_TEXT["PRZEGLĄD"][-1]:
            request.session["CURRENT_FLOW"] = "START"
            request.session["CURRENT_FLOW_NUM"] = 0

        request.session["CURRENT_FLOW_NUM"] += 1
        print(request.session["CHAT"])
        vr.redirect(reverse("gather_answer"), method="POST")
        

    
    # vr.say(answer.choices[0].message["content"], voice="alice", language="pl-PL") # type: ignore
    # request.session["CHAT"].append({"role": "assistant", "content": answer.choices[0].message["content"]}) # type: ignore
    print(request.session["CHAT"])
    return HttpResponse(str(vr))

def flow_prompt(request):
    prompt = """Sklasyfikuj temat rozmowy jako PRZEGLĄD (zapisanie klienta na przegląd), PYTANIA (odpowiedzenie o zapytanie o cenę podstawowych usług serwisowych) lub KONSULTANT (przekazanie rozmowy do konsultanta, jeżeli klient dzwoni w innej sprawie niż z tych, co wymienione):
KONWERSACJA: Dzień dobry, mam pytanie na temat ceny przeglądu samochodu. Ile kosztuje przegląd samochodu?
TEMAT: PYTANIA
KONWERSACJA: """
    for i in request.session["CHAT"]:
        prompt += i["content"] 
    prompt += "\nTEMAT: "
    return prompt