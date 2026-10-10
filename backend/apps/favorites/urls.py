from django.urls import path

from .views import (
    FavoriteCompanyDetailView,
    FavoriteCompanyListView,
    FavoriteIdsView,
    FavoriteJobDetailView,
    FavoriteJobListView,
)

urlpatterns = [
    path('candidate/favorites/ids/', FavoriteIdsView.as_view(), name='candidate-favorite-ids'),
    path('candidate/favorites/jobs/', FavoriteJobListView.as_view(), name='candidate-favorite-jobs'),
    path('candidate/favorites/jobs/<uuid:job_id>/', FavoriteJobDetailView.as_view(), name='candidate-favorite-job'),
    path('candidate/favorites/companies/', FavoriteCompanyListView.as_view(), name='candidate-favorite-companies'),
    path(
        'candidate/favorites/companies/<uuid:company_id>/', FavoriteCompanyDetailView.as_view(),
        name='candidate-favorite-company',
    ),
]
