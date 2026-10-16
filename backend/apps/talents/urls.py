from django.urls import path

from .views import SuggestedCandidatesView, TalentCVFileView, TalentPoolView

urlpatterns = [
    path('employer/talents/', TalentPoolView.as_view(), name='employer-talents'),
    path(
        'employer/jobs/<uuid:job_id>/suggested-candidates/', SuggestedCandidatesView.as_view(),
        name='employer-job-suggested-candidates',
    ),
    path('employer/talents/<uuid:candidate_id>/cv/', TalentCVFileView.as_view(), name='employer-talent-cv'),
]
