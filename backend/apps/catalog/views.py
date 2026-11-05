"""API danh mục công khai: tỉnh/thành phố, ngành nghề, kỹ năng (autocomplete)."""
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Industry, Location, Skill
from .serializers import IndustrySerializer, LocationSerializer, SkillSerializer

TAG = ['Catalog']


class _CatalogListView(generics.ListAPIView):
    """Danh mục công khai, ít thay đổi, trả về toàn bộ (không phân trang)."""

    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None
    filter_backends = []


class LocationListView(_CatalogListView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    # GET /api/v1/catalog/locations/
    @extend_schema(tags=TAG, summary='Danh sách tỉnh/thành phố', responses=LocationSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class IndustryListView(_CatalogListView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

    # GET /api/v1/catalog/industries/
    @extend_schema(tags=TAG, summary='Danh sách ngành nghề', responses=IndustrySerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SkillListView(_CatalogListView):
    serializer_class = SkillSerializer
    limit = 20

    def get_queryset(self):
        qs = Skill.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(aliases__icontains=search))
        return qs.order_by('-is_verified', 'name')[: self.limit]

    # GET /api/v1/catalog/skills/?search=   (tối đa 20 kỹ năng)
    @extend_schema(tags=TAG, summary='Gợi ý kỹ năng (autocomplete)',
                   parameters=[OpenApiParameter('search', str, description='Từ khóa, vd. "kế toán"')],
                   responses=SkillSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
