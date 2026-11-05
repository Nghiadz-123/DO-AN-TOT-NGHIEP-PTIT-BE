"""API tài khoản nhà tuyển dụng: đăng ký, hồ sơ cá nhân, hồ sơ công ty và logo."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts import services as account_services
from apps.accounts.serializers import SessionSerializer, UserSerializer
from common.views import validated_body

from . import services
from .permissions import CanManageCompany, EmployerAccessMixin, IsEmployer
from .serializers import (
    CompanyLogoSerializer,
    CompanySerializer,
    EmployerRegisterSerializer,
    RecruiterProfileSerializer,
)

ACCOUNT_TAG = ['Employer - Tài khoản']
COMPANY_TAG = ['Employer - Công ty']


class EmployerRegisterView(APIView):
    """Đăng ký tài khoản nhà tuyển dụng: tạo user, công ty và đăng nhập luôn."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    # POST /api/v1/employer/register/
    @extend_schema(tags=ACCOUNT_TAG, request=EmployerRegisterSerializer, responses={201: SessionSerializer})
    def post(self, request):
        body = validated_body(request, EmployerRegisterSerializer)
        recruiter = services.register_employer(**body)
        user_data = UserSerializer(recruiter.user, context={'request': request}).data
        return Response(
            {**account_services.issue_tokens(recruiter.user), 'user': user_data}, status=status.HTTP_201_CREATED
        )


class RecruiterProfileView(EmployerAccessMixin, APIView):
    """Hồ sơ cá nhân của nhà tuyển dụng đang đăng nhập."""

    # GET /api/v1/employer/profile/
    @extend_schema(tags=ACCOUNT_TAG, responses=RecruiterProfileSerializer)
    def get(self, request):
        return Response(RecruiterProfileSerializer(self.recruiter, context={'request': request}).data)

    # PATCH /api/v1/employer/profile/
    @extend_schema(tags=ACCOUNT_TAG, request=RecruiterProfileSerializer, responses=RecruiterProfileSerializer)
    def patch(self, request):
        body = validated_body(request, RecruiterProfileSerializer, instance=self.recruiter, partial=True)
        user_fields = body.get('user', {})
        recruiter = services.update_recruiter_profile(
            self.recruiter,
            full_name=user_fields.get('full_name'),
            phone=user_fields.get('phone'),
            position=body.get('position'),
        )
        return Response(RecruiterProfileSerializer(recruiter, context={'request': request}).data)


class CompanyView(EmployerAccessMixin, APIView):
    """Hồ sơ công ty. Mọi recruiter xem được; owner/admin của công ty được sửa."""

    permission_classes = [IsEmployer, CanManageCompany]

    # GET /api/v1/employer/company/
    @extend_schema(tags=COMPANY_TAG, responses=CompanySerializer)
    def get(self, request):
        return Response(CompanySerializer(self.company, context={'request': request}).data)

    # PATCH /api/v1/employer/company/
    @extend_schema(tags=COMPANY_TAG, request=CompanySerializer, responses=CompanySerializer)
    def patch(self, request):
        body = validated_body(request, CompanySerializer, instance=self.company, partial=True)
        company = services.update_company(self.company, data=body)
        return Response(CompanySerializer(company, context={'request': request}).data)


class CompanyLogoView(EmployerAccessMixin, APIView):
    """Tải lên (multipart, trường `logo`: jpg/png/webp, tối đa 2 MB) hoặc xóa logo công ty."""

    permission_classes = [IsEmployer, CanManageCompany]
    parser_classes = [MultiPartParser, FormParser]

    # POST /api/v1/employer/company/logo/   (multipart/form-data)
    @extend_schema(tags=COMPANY_TAG, request=CompanyLogoSerializer, responses=CompanySerializer)
    def post(self, request):
        body = validated_body(request, CompanyLogoSerializer)
        company = services.set_company_logo(self.company, body['logo'])
        return Response(CompanySerializer(company, context={'request': request}).data)

    # DELETE /api/v1/employer/company/logo/
    @extend_schema(tags=COMPANY_TAG, request=None, responses=CompanySerializer)
    def delete(self, request):
        company = services.remove_company_logo(self.company)
        return Response(CompanySerializer(company, context={'request': request}).data)
