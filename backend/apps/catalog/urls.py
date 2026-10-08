from django.urls import path

from .views import IndustryListView, LocationListView, SkillListView

urlpatterns = [
    path('catalog/locations/', LocationListView.as_view(), name='catalog-locations'),
    path('catalog/industries/', IndustryListView.as_view(), name='catalog-industries'),
    path('catalog/skills/', SkillListView.as_view(), name='catalog-skills'),
]
