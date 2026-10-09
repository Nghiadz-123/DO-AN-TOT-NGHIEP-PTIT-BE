from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CandidateApplicationViewSet, EmployerApplicationViewSet, EmployerDashboardView

router = SimpleRouter()
router.register('employer/applications', EmployerApplicationViewSet, basename='employer-application')
router.register('candidate/applications', CandidateApplicationViewSet, basename='candidate-application')

urlpatterns = [
    path('employer/dashboard/', EmployerDashboardView.as_view(), name='employer-dashboard'),
    *router.urls,
]
