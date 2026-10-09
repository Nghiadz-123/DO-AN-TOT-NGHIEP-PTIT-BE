from rest_framework.routers import SimpleRouter

from .views import CandidateCVViewSet

router = SimpleRouter()
router.register('candidate/cvs', CandidateCVViewSet, basename='candidate-cv')

urlpatterns = router.urls
