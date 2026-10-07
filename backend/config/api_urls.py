"""Gom URL của các app vào /api/v1/.

Mỗi app tự khai báo đường dẫn đầy đủ của mình trong urls.py (vd. 'employer/jobs/').
Thêm module mới (vd. apps.ai ở giai đoạn sau) chỉ cần thêm một dòng include.
"""
from django.urls import include, path

urlpatterns = [
    path('', include('apps.accounts.urls')),      # auth/...
    path('', include('apps.catalog.urls')),       # catalog/...
    path('', include('apps.employers.urls')),     # employer/register|profile|company
    path('', include('apps.jobs.urls')),          # employer/jobs/..., jobs/... (công khai)
    path('', include('apps.applications.urls')),  # employer/applications/..., employer/dashboard/
]
