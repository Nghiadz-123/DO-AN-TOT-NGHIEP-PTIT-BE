from rest_framework.routers import SimpleRouter

from .views import EmployerJobViewSet, PublicCompanyViewSet, PublicJobViewSet

router = SimpleRouter()
router.register('employer/jobs', EmployerJobViewSet, basename='employer-job')
router.register('jobs', PublicJobViewSet, basename='public-job')
router.register('companies', PublicCompanyViewSet, basename='public-company')

urlpatterns = router.urls
