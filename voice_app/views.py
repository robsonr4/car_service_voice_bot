from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import SuspiciousOperation
from twilio.request_validator import RequestValidator
from django.http import HttpRequest, HttpResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.http import Response
from django.urls import reverse

# from .decorators import validate_twilio_request

# @validate_twilio_request
@require_POST
@csrf_exempt
def greet_client(request: HttpRequest):
    """ Greet the caller and tranfer them to particular conversation flow.
    """
    vr = VoiceResponse()
    vr.say("Cześć, to jest automatyczna sekretarka serwisu Lexusa, Toyoty, Sciona. W czym mógłbym Państwu dzisiaj pomóc?", voice="alice", language="pl-PL")
    
    reverse("/present_prompts/")
    return HttpResponse(str(vr))

@require_POST
@csrf_exempt
def gather_answer(request: HttpRequest):
    vr = VoiceResponse()
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
    vr.say("Możesz mnie poprosić o zapisanie na przegląd lub zapytanie o cenę podstawowych usług serwisowych.", voice="alice", language="pl-PL")
    vr.say("Jeżeli dzwonisz w innej sprawie niż z tych, co wymieniłem, poproś o rozmowę z konsultantem.", voice="alice", language="pl-PL")
    reverse("/gather_answer/")
    return HttpResponse(str(vr))

@require_POST
@csrf_exempt
def transfer_to_flow(request: HttpRequest):
    """ Transfer the caller to particular conversation flow.
    """
    vr = VoiceResponse()
    print(request.POST)
    return HttpResponse(str(vr))