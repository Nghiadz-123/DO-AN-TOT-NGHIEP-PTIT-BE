from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts import services as account_services
from apps.accounts.serializers import SessionSerializer, UserSerializer

from . import services
from .permissions import CanManageCompany, EmployerAccessMixin, IsEmployer
from .serializers import (
    CompanyLogoSerializer,
    CompanySerializer,
    EmployerRegisterSerializer,
    RecruiterProfileSerializer,
)


class EmployerRegisterView(APIView):
    """Đăng ký tài khoản nhà tuyển dụng: tạo user, công ty và đăng nhập luôn."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    @extend_schema(tags=['Employer - Tài khoản'], request=EmployerRegisterSerializer, responses={201: SessionSerializer})
    def post(self, request):
        serializer = EmployerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recruiter = services.register_employer(**serializer.validated_data)
        user_data = UserSerializer(recruiter.user, context={'request': request}).data
        return Response(
            {**account_services.issue_tokens(recruiter.user), 'user': user_data}, status=status.HTTP_201_CREATED
        )


class RecruiterProfileView(EmployerAccessMixin, APIView):
    """Hồ sơ cá nhân của nhà tuyển dụng đang đăng nhập."""

    @extend_schema(tags=['Employer - Tài khoản'], responses=RecruiterProfileSerializer)
    def get(self, request):
        return Response(RecruiterProfileSerializer(self.recruiter, context={'request': request}).data)

    @extend_schema(tags=['Employer - Tài khoản'], request=RecruiterProfileSerializer, responses=RecruiterProfileSerializer)
    def patch(self, request):
        serializer = RecruiterProfileSerializer(self.recruiter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        recruiter = services.update_recruiter_profile(
            self.recruiter,
            full_name=data.get('user', {}).get('full_name'),
            phone=data.get('user', {}).get('phone'),
            position=data.get('position'),
        )
        return Response(RecruiterProfileSerializer(recruiter, context={'request': request}).data)


class CompanyView(EmployerAccessMixin, APIView):
    """Hồ sơ công ty. Mọi recruiter xem được; owner/admin của công ty được sửa."""

    permission_classes = [IsEmployer, CanManageCompany]

    @extend_schema(tags=['Employer - Công ty'], responses=CompanySerializer)
    def get(self, request):
        return Response(CompanySerializer(self.company, context={'request': request}).data)

    @extend_schema(tags=['Employer - Công ty'], request=CompanySerializer, responses=CompanySerializer)
    def patch(self, request):
        serializer = CompanySerializer(self.company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        company = services.update_company(self.company, data=serializer.validated_data)
        return Response(CompanySerializer(company, context={'request': request}).data)


class CompanyLogoView(EmployerAccessMixin, APIView):
    """Tải lên (multipart, trường `logo`: jpg/png/webp, tối đa 2 MB) hoặc xóa logo công ty."""

    permission_classes = [IsEmployer, CanManageCompany]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(tags=['Employer - Công ty'], request=CompanyLogoSerializer, responses=CompanySerializer)
    def post(self, request):
        serializer = CompanyLogoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = services.set_company_logo(self.company, serializer.validated_data['logo'])
        return Response(CompanySerializer(company, context={'request': request}).data)

    @extend_schema(tags=['Employer - Công ty'], request=None, responses=CompanySerializer)
    def delete(self, request):
        company = services.remove_company_logo(self.company)
        return Response(CompanySerializer(company, context={'request': request}).data)
