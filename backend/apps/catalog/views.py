from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Industry, Location, Skill
from .serializers import IndustrySerializer, LocationSerializer, SkillSerializer


class _CatalogListView(generics.ListAPIView):
    """Danh mục công khai, ít thay đổi, trả về toàn bộ (không phân trang)."""

    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None
    filter_backends = []


@extend_schema_view(get=extend_schema(tags=['Catalog'], summary='Danh sách tỉnh/thành phố'))
class LocationListView(_CatalogListView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


@extend_schema_view(get=extend_schema(tags=['Catalog'], summary='Danh sách ngành nghề'))
class IndustryListView(_CatalogListView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Catalog'],
        summary='Gợi ý kỹ năng (autocomplete)',
        parameters=[OpenApiParameter('search', str, description='Từ khóa, vd. "rea"')],
    )
)
class SkillListView(_CatalogListView):
    serializer_class = SkillSerializer
    limit = 20

    def get_queryset(self):
        qs = Skill.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(aliases__icontains=search))
        return qs.order_by('-is_verified', 'name')[: self.limit]
