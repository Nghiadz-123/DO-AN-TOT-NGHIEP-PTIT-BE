from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
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


class SsoAdminView(APIView):
    """Tự động đăng nhập vào Django Admin bằng JWT token từ frontend."""

    permission_classes = [AllowAny]

    def get(self, request):
        from django.contrib.auth import login as django_login
        from django.shortcuts import redirect
        from rest_framework_simplejwt.tokens import AccessToken
        from .models import User

        token_str = request.query_params.get('token')
        if not token_str:
            return redirect('/admin/')
        try:
            token = AccessToken(token_str)
            user = User.objects.get(id=token['user_id'], is_active=True)
            if user.is_staff or user.is_superuser:
                django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/admin/')
        except Exception:
            pass
        return redirect('/admin/')


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin'))


class AdminOverviewView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        from apps.employers.models import Company, VerificationStatus
        from apps.jobs.models import Job, JobStatus
        from apps.applications.models import Application
        from .models import User, UserRole

        total_users = User.objects.count()
        candidates_count = User.objects.filter(role=UserRole.CANDIDATE).count()
        employers_count = User.objects.filter(role=UserRole.EMPLOYER).count()
        total_companies = Company.objects.count()
        pending_companies = Company.objects.filter(verification_status=VerificationStatus.PENDING).count()
        total_jobs = Job.objects.count()
        published_jobs = Job.objects.filter(status=JobStatus.PUBLISHED).count()
        total_applications = Application.objects.count()

        recent_users = list(
            User.objects.order_by('-created_at')[:5].values(
                'id', 'email', 'full_name', 'role', 'is_active', 'created_at'
            )
        )
        recent_companies = list(
            Company.objects.order_by('-created_at')[:5].values(
                'id', 'name', 'tax_code', 'verification_status', 'created_at'
            )
        )

        return Response({
            'total_users': total_users,
            'candidates_count': candidates_count,
            'employers_count': employers_count,
            'total_companies': total_companies,
            'pending_companies': pending_companies,
            'total_jobs': total_jobs,
            'published_jobs': published_jobs,
            'total_applications': total_applications,
            'recent_users': recent_users,
            'recent_companies': recent_companies,
        })


class AdminUsersView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        from .models import User
        role = request.query_params.get('role')
        search = request.query_params.get('q', '').strip()
        qs = User.objects.all().order_by('-created_at')
        if role:
            qs = qs.filter(role=role)
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(email__icontains=search) | Q(full_name__icontains=search) | Q(phone__icontains=search))

        users_data = list(qs[:100].values('id', 'email', 'full_name', 'phone', 'role', 'is_active', 'is_staff', 'created_at'))
        return Response({'results': users_data, 'count': qs.count()})

    def patch(self, request, user_id):
        from .models import User, UserRole
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Người dùng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        if 'is_active' in request.data:
            target_user.is_active = bool(request.data['is_active'])
        if 'role' in request.data and request.data['role'] in UserRole.values:
            target_user.role = request.data['role']
        target_user.save()
        return Response({
            'id': target_user.id,
            'email': target_user.email,
            'full_name': target_user.full_name,
            'phone': target_user.phone,
            'role': target_user.role,
            'is_active': target_user.is_active,
            'is_staff': target_user.is_staff,
            'created_at': target_user.created_at,
        })


class AdminCompaniesView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        from apps.employers.models import Company
        status_filter = request.query_params.get('status')
        search = request.query_params.get('q', '').strip()
        qs = Company.objects.all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(verification_status=status_filter)
        if search:
            qs = qs.filter(name__icontains=search)

        data = []
        for c in qs[:100]:
            data.append({
                'id': str(c.id),
                'name': c.name,
                'tax_code': c.tax_code or '',
                'verification_status': c.verification_status,
                'phone': c.phone or '',
                'email': c.email or '',
                'website': c.website or '',
                'created_at': c.created_at,
            })
        return Response({'results': data, 'count': qs.count()})

    def patch(self, request, company_id):
        from apps.employers.models import Company, VerificationStatus
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'detail': 'Công ty không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('verification_status')
        if new_status in VerificationStatus.values:
            company.verification_status = new_status
            company.save(update_fields=['verification_status', 'updated_at'])
            return Response({'id': str(company.id), 'name': company.name, 'verification_status': company.verification_status})
        return Response({'detail': 'Trạng thái không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)


class AdminJobsView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        from apps.jobs.models import Job
        search = request.query_params.get('q', '').strip()
        status_filter = request.query_params.get('status')
        qs = Job.objects.select_related('company').all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(title__icontains=search)

        data = []
        for j in qs[:100]:
            data.append({
                'id': str(j.id),
                'title': j.title,
                'company_name': j.company.name if j.company else '',
                'status': j.status,
                'job_type': j.job_type,
                'level': j.level,
                'created_at': j.created_at,
            })
        return Response({'results': data, 'count': qs.count()})

    def patch(self, request, job_id):
        from apps.jobs.models import Job, JobStatus
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'detail': 'Tin tuyển dụng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status in JobStatus.values:
            job.status = new_status
            job.save(update_fields=['status', 'updated_at'])
            return Response({'id': str(job.id), 'title': job.title, 'status': job.status})
        return Response({'detail': 'Trạng thái không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)
