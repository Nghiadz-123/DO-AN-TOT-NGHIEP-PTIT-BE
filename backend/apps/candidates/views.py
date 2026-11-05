"""API tài khoản ứng viên: đăng ký và hồ sơ (thông tin cá nhân, mong muốn công việc)."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts import services as account_services
from apps.accounts.serializers import SessionSerializer, UserSerializer
from common.views import validated_body

from . import services
from .permissions import CandidateAccessMixin
from .serializers import CandidateProfileSerializer, CandidateRegisterSerializer

TAG = ['Candidate - Tài khoản']


class CandidateRegisterView(APIView):
    """Đăng ký tài khoản ứng viên: tạo user, hồ sơ rỗng và đăng nhập luôn."""

    permission_classes = [AllowAny]
    authentication_classes = []  # bỏ qua token cũ (hết hạn) frontend còn giữ, như API công khai
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    # POST /api/v1/candidate/register/
    @extend_schema(tags=TAG, request=CandidateRegisterSerializer, responses={201: SessionSerializer})
    def post(self, request):
        body = validated_body(request, CandidateRegisterSerializer)
        profile = services.register_candidate(**body)
        user_data = UserSerializer(profile.user, context={'request': request}).data
        return Response(
            {**account_services.issue_tokens(profile.user), 'user': user_data}, status=status.HTTP_201_CREATED
        )


class CandidateProfileView(CandidateAccessMixin, APIView):
    """Hồ sơ của ứng viên đang đăng nhập: thông tin cá nhân và mong muốn công việc."""

    # GET /api/v1/candidate/profile/
    @extend_schema(tags=TAG, responses=CandidateProfileSerializer)
    def get(self, request):
        return Response(CandidateProfileSerializer(self.candidate, context={'request': request}).data)

    # PATCH /api/v1/candidate/profile/
    @extend_schema(tags=TAG, request=CandidateProfileSerializer, responses=CandidateProfileSerializer)
    def patch(self, request):
        body = validated_body(request, CandidateProfileSerializer, instance=self.candidate, partial=True)
        user_fields = body.pop('user', {})
        profile = services.update_candidate_profile(
            self.candidate, data=body, full_name=user_fields.get('full_name'), phone=user_fields.get('phone')
        )
        return Response(CandidateProfileSerializer(profile, context={'request': request}).data)
