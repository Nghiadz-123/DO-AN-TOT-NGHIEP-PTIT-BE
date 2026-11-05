"""API tài khoản: đăng nhập / đăng xuất bằng JWT, thông tin tài khoản, đổi mật khẩu, SSO vào Django Admin.

Làm mới token (POST /api/v1/auth/token/refresh/) dùng thẳng TokenRefreshView của simplejwt, khai báo ở urls.py.
"""
from django.contrib.auth import login as django_login
from django.shortcuts import redirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from common.views import validated_body

from . import services
from .serializers import (
    AccountUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    SessionSerializer,
    TokenPairSerializer,
    UserSerializer,
)

TAG = ['Auth']


# POST /api/v1/auth/login/
@extend_schema(tags=TAG, request=LoginSerializer, responses=SessionSerializer)
class LoginView(TokenObtainPairView):
    """Đăng nhập bằng email + mật khẩu, trả về access/refresh token và thông tin user."""

    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class LogoutView(APIView):
    """Thu hồi refresh token (đưa vào blacklist). Không yêu cầu access token còn hạn."""

    permission_classes = [AllowAny]

    # POST /api/v1/auth/logout/
    @extend_schema(tags=TAG, request=LogoutSerializer, responses={204: None})
    def post(self, request):
        body = validated_body(request, LogoutSerializer)
        services.logout(body['refresh'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/v1/auth/me/
    @extend_schema(tags=TAG, responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    # PATCH /api/v1/auth/me/
    @extend_schema(tags=TAG, request=AccountUpdateSerializer, responses=UserSerializer)
    def patch(self, request):
        body = validated_body(request, AccountUpdateSerializer, partial=True)
        user = services.update_account(request.user, **body)
        return Response(UserSerializer(user, context={'request': request}).data)


class ChangePasswordView(APIView):
    """Đổi mật khẩu. Mọi phiên đăng nhập cũ bị thu hồi; response chứa token mới cho phiên hiện tại."""

    permission_classes = [IsAuthenticated]

    # POST /api/v1/auth/change-password/
    @extend_schema(tags=TAG, request=ChangePasswordSerializer, responses=TokenPairSerializer)
    def post(self, request):
        body = validated_body(request, ChangePasswordSerializer)
        tokens = services.change_password(request.user, **body)
        return Response(tokens)


class SsoAdminView(APIView):
    """Tự động đăng nhập vào Django Admin bằng JWT token từ frontend."""

    permission_classes = [AllowAny]

    # GET /api/v1/auth/sso-admin/?token=<access token>
    @extend_schema(
        tags=TAG,
        summary='Đăng nhập Django Admin bằng access token rồi chuyển tới /admin/',
        description='Token hợp lệ của tài khoản staff: tạo phiên Django Admin. Mọi trường hợp đều chuyển hướng tới /admin/.',
        parameters=[OpenApiParameter('token', OpenApiTypes.STR, description='Access token JWT')],
        responses={302: OpenApiResponse(description='Chuyển hướng tới /admin/')},
    )
    def get(self, request):
        user = services.staff_user_from_token(request.query_params.get('token', ''))
        if user is not None:
            django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/admin/')
