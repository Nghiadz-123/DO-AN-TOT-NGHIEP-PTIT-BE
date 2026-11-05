"""API yêu thích của ứng viên: việc làm và công ty. Thêm / bỏ lặp lại không lỗi (bấm hai lần, hai tab cùng lúc)."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidates.permissions import CandidateAccessMixin
from apps.employers.models import Company
from apps.jobs.models import Job
from common.views import validated_body

from . import selectors, services
from .serializers import (
    FavoriteCompanyCreateSerializer,
    FavoriteCompanySerializer,
    FavoriteIdsSerializer,
    FavoriteJobCreateSerializer,
    FavoriteJobSerializer,
)

TAG = ['Candidate - Yêu thích']


class FavoriteIdsView(CandidateAccessMixin, APIView):
    # GET /api/v1/candidate/favorites/ids/
    @extend_schema(tags=TAG, summary='Id các tin / công ty đang yêu thích (để đánh dấu nút yêu thích)',
                   responses=FavoriteIdsSerializer)
    def get(self, request):
        return Response(FavoriteIdsSerializer(selectors.favorite_ids(self.candidate)).data)


class FavoriteJobListView(CandidateAccessMixin, generics.ListAPIView):
    """Việc làm yêu thích của ứng viên đang đăng nhập."""

    serializer_class = FavoriteJobSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Job.objects.none()
        return selectors.favorite_jobs(self.candidate)

    # GET /api/v1/candidate/favorites/jobs/?page=
    @extend_schema(tags=TAG, summary='Việc làm yêu thích (mới thêm trước, phân trang)',
                   responses=FavoriteJobSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # POST /api/v1/candidate/favorites/jobs/
    @extend_schema(tags=TAG, summary='Thêm tin vào yêu thích (đã có thì trả 200)',
                   request=FavoriteJobCreateSerializer, responses={201: FavoriteJobSerializer, 200: FavoriteJobSerializer})
    def post(self, request):
        job = validated_body(request, FavoriteJobCreateSerializer)['job']
        created = services.add_favorite_job(self.candidate, job)
        data = self.get_serializer(self.get_queryset().get(pk=job.pk)).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class FavoriteJobDetailView(CandidateAccessMixin, APIView):
    # DELETE /api/v1/candidate/favorites/jobs/{job_id}/
    @extend_schema(tags=TAG, summary='Bỏ yêu thích một tin (theo id tin; chưa yêu thích cũng trả 204)',
                   responses={204: None})
    def delete(self, request, job_id):
        services.remove_favorite_job(self.candidate, job_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteCompanyListView(CandidateAccessMixin, generics.ListAPIView):
    """Công ty yêu thích của ứng viên đang đăng nhập."""

    serializer_class = FavoriteCompanySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Company.objects.none()
        return selectors.favorite_companies(self.candidate)

    # GET /api/v1/candidate/favorites/companies/?page=
    @extend_schema(tags=TAG, summary='Công ty yêu thích (mới thêm trước, phân trang)',
                   responses=FavoriteCompanySerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # POST /api/v1/candidate/favorites/companies/
    @extend_schema(tags=TAG, summary='Thêm công ty vào yêu thích (đã có thì trả 200)',
                   request=FavoriteCompanyCreateSerializer,
                   responses={201: FavoriteCompanySerializer, 200: FavoriteCompanySerializer})
    def post(self, request):
        company = validated_body(request, FavoriteCompanyCreateSerializer)['company']
        created = services.add_favorite_company(self.candidate, company)
        data = self.get_serializer(self.get_queryset().get(pk=company.pk)).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class FavoriteCompanyDetailView(CandidateAccessMixin, APIView):
    # DELETE /api/v1/candidate/favorites/companies/{company_id}/
    @extend_schema(tags=TAG, summary='Bỏ yêu thích một công ty (theo id công ty; chưa yêu thích cũng trả 204)',
                   responses={204: None})
    def delete(self, request, company_id):
        services.remove_favorite_company(self.candidate, company_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
