from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import EmployerApplicationViewSet, EmployerDashboardView

router = SimpleRouter()
router.register('employer/applications', EmployerApplicationViewSet, basename='employer-application')

urlpatterns = [
    path('employer/dashboard/', EmployerDashboardView.as_view(), name='employer-dashboard'),
    *router.urls,
]
