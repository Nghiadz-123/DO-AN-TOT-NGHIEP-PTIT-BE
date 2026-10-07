from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

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


@extend_schema(tags=['Auth'], responses=SessionSerializer)
class LoginView(TokenObtainPairView):
    """Đăng nhập bằng email + mật khẩu, trả về access/refresh token và thông tin user."""

    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class LogoutView(APIView):
    """Thu hồi refresh token (đưa vào blacklist). Không yêu cầu access token còn hạn."""

    permission_classes = [AllowAny]

    @extend_schema(tags=['Auth'], request=LogoutSerializer, responses={204: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.logout(serializer.validated_data['refresh'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    @extend_schema(tags=['Auth'], request=AccountUpdateSerializer, responses=UserSerializer)
    def patch(self, request):
        serializer = AccountUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = services.update_account(request.user, **serializer.validated_data)
        return Response(UserSerializer(user, context={'request': request}).data)


class ChangePasswordView(APIView):
    """Đổi mật khẩu. Mọi phiên đăng nhập cũ bị thu hồi; response chứa token mới cho phiên hiện tại."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], request=ChangePasswordSerializer, responses=TokenPairSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        tokens = services.change_password(request.user, **serializer.validated_data)
        return Response(tokens)
