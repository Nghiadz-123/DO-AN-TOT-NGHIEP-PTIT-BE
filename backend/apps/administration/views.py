"""API trang quản trị hệ thống (frontend: các trang /admin). Chỉ admin hệ thống: role admin hoặc is_staff.

- AdminOverviewView                                số liệu tổng quan
- AdminUserListView / AdminUserDetailView          người dùng: danh sách, khóa / mở khóa, đổi vai trò
- AdminCompanyListView / AdminCompanyDetailView    doanh nghiệp: danh sách, xác minh
- AdminJobListView / AdminJobDetailView            tin tuyển dụng: danh sách, đổi trạng thái

Danh sách chưa phân trang: `results` gồm tối đa LIST_LIMIT mục mới nhất, `count` là tổng số khớp bộ lọc.
"""
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from common.views import validated_body, validated_query

from . import selectors, services
from .permissions import IsSystemAdmin
from .serializers import (
    AdminCompanyListSerializer,
    AdminCompanyQuerySerializer,
    AdminCompanyStatusSerializer,
    AdminCompanyUpdateSerializer,
    AdminJobListSerializer,
    AdminJobQuerySerializer,
    AdminJobStatusSerializer,
    AdminJobUpdateSerializer,
    AdminOverviewSerializer,
    AdminUserListSerializer,
    AdminUserQuerySerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
)

TAG = ['Admin']


def _newest(queryset) -> dict:
    return {'results': queryset[:selectors.LIST_LIMIT], 'count': queryset.count()}


class _AdminView(APIView):
    permission_classes = [IsSystemAdmin]


class AdminOverviewView(_AdminView):
    # GET /api/v1/admin/overview/
    @extend_schema(tags=TAG, summary='Số liệu tổng quan, người dùng và doanh nghiệp mới nhất',
                   responses=AdminOverviewSerializer)
    def get(self, request):
        return Response(AdminOverviewSerializer(selectors.overview()).data)


# ============================================================================ người dùng
class AdminUserListView(_AdminView):
    # GET /api/v1/admin/users/?role=&q=
    @extend_schema(tags=TAG, summary='Danh sách người dùng (mới nhất trước)', parameters=[AdminUserQuerySerializer],
                   responses=AdminUserListSerializer)
    def get(self, request):
        query = validated_query(request, AdminUserQuerySerializer)
        users = selectors.users(role=query['role'], search=query['q'])
        return Response(AdminUserListSerializer(_newest(users)).data)


class AdminUserDetailView(_AdminView):
    # PATCH /api/v1/admin/users/{user_id}/
    @extend_schema(tags=TAG, summary='Khóa / mở khóa tài khoản, đổi vai trò', request=AdminUserUpdateSerializer,
                   responses=AdminUserSerializer)
    def patch(self, request, user_id):
        user = selectors.get_user(user_id)
        if user is None:
            raise NotFound('Người dùng không tồn tại.')
        body = validated_body(request, AdminUserUpdateSerializer, partial=True)
        user = services.update_user(user, **body)
        return Response(AdminUserSerializer(user).data)


# ============================================================================ doanh nghiệp
class AdminCompanyListView(_AdminView):
    # GET /api/v1/admin/companies/?status=&q=
    @extend_schema(tags=TAG, summary='Danh sách doanh nghiệp (mới nhất trước)', parameters=[AdminCompanyQuerySerializer],
                   responses=AdminCompanyListSerializer)
    def get(self, request):
        query = validated_query(request, AdminCompanyQuerySerializer)
        companies = selectors.companies(verification_status=query['status'], search=query['q'])
        return Response(AdminCompanyListSerializer(_newest(companies)).data)


class AdminCompanyDetailView(_AdminView):
    # PATCH /api/v1/admin/companies/{company_id}/
    @extend_schema(tags=TAG, summary='Xác minh / từ chối xác minh doanh nghiệp', request=AdminCompanyUpdateSerializer,
                   responses=AdminCompanyStatusSerializer)
    def patch(self, request, company_id):
        company = selectors.get_company(company_id)
        if company is None:
            raise NotFound('Công ty không tồn tại.')
        body = validated_body(request, AdminCompanyUpdateSerializer)
        company = services.set_company_verification(company, body['verification_status'])
        return Response(AdminCompanyStatusSerializer(company).data)


# ============================================================================ tin tuyển dụng
class AdminJobListView(_AdminView):
    # GET /api/v1/admin/jobs/?status=&q=
    @extend_schema(tags=TAG, summary='Danh sách tin tuyển dụng của mọi công ty (mới nhất trước)',
                   parameters=[AdminJobQuerySerializer], responses=AdminJobListSerializer)
    def get(self, request):
        query = validated_query(request, AdminJobQuerySerializer)
        jobs = selectors.jobs(status=query['status'], search=query['q'])
        return Response(AdminJobListSerializer(_newest(jobs)).data)


class AdminJobDetailView(_AdminView):
    # PATCH /api/v1/admin/jobs/{job_id}/
    @extend_schema(tags=TAG, summary='Đổi trạng thái tin (vd. đóng tin, mở lại tin tạm dừng)',
                   request=AdminJobUpdateSerializer, responses=AdminJobStatusSerializer)
    def patch(self, request, job_id):
        job = selectors.get_job(job_id)
        if job is None:
            raise NotFound('Tin tuyển dụng không tồn tại.')
        body = validated_body(request, AdminJobUpdateSerializer)
        job = services.set_job_status(job, body['status'])
        return Response(AdminJobStatusSerializer(job).data)
