from rest_framework.routers import SimpleRouter

from .views import EmployerJobViewSet, PublicJobViewSet

router = SimpleRouter()
router.register('employer/jobs', EmployerJobViewSet, basename='employer-job')
router.register('jobs', PublicJobViewSet, basename='public-job')

urlpatterns = router.urls
