from django.urls import path

from .views import CandidateProfileView, CandidateRegisterView

urlpatterns = [
    path('candidate/register/', CandidateRegisterView.as_view(), name='candidate-register'),
    path('candidate/profile/', CandidateProfileView.as_view(), name='candidate-profile'),
]
