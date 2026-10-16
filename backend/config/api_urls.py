"""Gom URL của các app vào /api/v1/.

Mỗi app tự khai báo đường dẫn đầy đủ của mình trong urls.py (vd. 'employer/jobs/', 'candidate/cvs/').
Thêm module mới chỉ cần thêm một dòng include.
"""
from django.urls import include, path

urlpatterns = [
    path('', include('apps.accounts.urls')),      # auth/...
    path('', include('apps.catalog.urls')),       # catalog/...
    path('', include('apps.employers.urls')),     # employer/register|profile|company
    path('', include('apps.candidates.urls')),    # candidate/register|profile
    path('', include('apps.cvs.urls')),           # candidate/cvs/...
    path('', include('apps.jobs.urls')),          # employer/jobs/..., jobs/..., companies/... (công khai)
    path('', include('apps.applications.urls')),  # employer/applications/..., employer/dashboard/, candidate/applications/...
    path('', include('apps.favorites.urls')),     # candidate/favorites/...
    path('', include('apps.talents.urls')),       # employer/talents/..., employer/jobs/{id}/suggested-candidates/
    path('', include('apps.invitations.urls')),   # employer/invitations/..., candidate/invitations/... (thư mời)
    path('', include('apps.ai.urls')),            # candidate/cv-analyses/, candidate/cvs/{id}/analysis|recommended-jobs/...
]
