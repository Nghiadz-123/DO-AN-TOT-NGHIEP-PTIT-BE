from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CandidateCVBuilderView, CandidateCVViewSet

router = SimpleRouter()
router.register('candidate/cvs', CandidateCVViewSet, basename='candidate-cv')

urlpatterns = router.urls
urlpatterns += [path('candidate/cv-builder/', CandidateCVBuilderView.as_view(), name='candidate-cv-builder')]
