from rest_framework.routers import SimpleRouter

from .views import ConnectionViewSet

router = SimpleRouter()
router.register('connections', ConnectionViewSet, basename='connection')

urlpatterns = router.urls
