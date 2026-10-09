from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts import services as account_services
from apps.accounts.serializers import SessionSerializer, UserSerializer

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

    @extend_schema(tags=TAG, request=CandidateRegisterSerializer, responses={201: SessionSerializer})
    def post(self, request):
        serializer = CandidateRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = services.register_candidate(**serializer.validated_data)
        user_data = UserSerializer(profile.user, context={'request': request}).data
        return Response(
            {**account_services.issue_tokens(profile.user), 'user': user_data}, status=status.HTTP_201_CREATED
        )


class CandidateProfileView(CandidateAccessMixin, APIView):
    """Hồ sơ của ứng viên đang đăng nhập: thông tin cá nhân và mong muốn công việc."""

    @extend_schema(tags=TAG, responses=CandidateProfileSerializer)
    def get(self, request):
        return Response(CandidateProfileSerializer(self.candidate, context={'request': request}).data)

    @extend_schema(tags=TAG, request=CandidateProfileSerializer, responses=CandidateProfileSerializer)
    def patch(self, request):
        serializer = CandidateProfileSerializer(self.candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        user_data = data.pop('user', {})
        profile = services.update_candidate_profile(
            self.candidate, data=data, full_name=user_data.get('full_name'), phone=user_data.get('phone')
        )
        return Response(CandidateProfileSerializer(profile, context={'request': request}).data)
