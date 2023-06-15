from django.urls import path
from . import views

urlpatterns = [
    path("greet_client/", views.greet_client, name="greet_client"),
    path("transfer_to_flow/", views.transfer_to_flow, name="transfer_to_flow"),
    path("gather_answer/<str:st>/", views.gather_answer, name="gather_answer"),
    path("gather_answer/", views.gather_answer, name="gather_answer"),
    path("present_prompts/", views.present_prompts, name="present_prompts"),
    
]
