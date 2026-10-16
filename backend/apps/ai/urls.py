from django.urls import path

from .views import CVAnalysisListView, CVScoreView, CVSuggestionView, JobEvaluationView, RecommendedJobsView

urlpatterns = [
    path('candidate/cv-analyses/', CVAnalysisListView.as_view(), name='candidate-cv-analyses'),
    path('candidate/cvs/<uuid:cv_id>/analysis/score/', CVScoreView.as_view(), name='candidate-cv-score'),
    path(
        'candidate/cvs/<uuid:cv_id>/analysis/suggestions/', CVSuggestionView.as_view(),
        name='candidate-cv-suggestions',
    ),
    path(
        'candidate/cvs/<uuid:cv_id>/recommended-jobs/', RecommendedJobsView.as_view(),
        name='candidate-cv-recommended-jobs',
    ),
    path(
        'candidate/cvs/<uuid:cv_id>/recommended-jobs/<uuid:job_id>/evaluate/', JobEvaluationView.as_view(),
        name='candidate-cv-job-evaluation',
    ),
]
