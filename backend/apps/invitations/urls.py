from rest_framework.routers import SimpleRouter

from .views import CandidateInvitationViewSet, EmployerInvitationViewSet

router = SimpleRouter()
router.register('employer/invitations', EmployerInvitationViewSet, basename='employer-invitation')
router.register('candidate/invitations', CandidateInvitationViewSet, basename='candidate-invitation')

urlpatterns = router.urls
