from rest_framework.routers import DefaultRouter
from .views import TradeCategoryViewSet, ProfessionalProfileViewSet, ProfessionalCoverageAreaViewSet

router = DefaultRouter()
router.register(r'trades', TradeCategoryViewSet)
router.register(r'profiles', ProfessionalProfileViewSet)
router.register(r'coverage-areas', ProfessionalCoverageAreaViewSet)

professionals_router = router
urlpatterns = router.urls