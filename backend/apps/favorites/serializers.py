from rest_framework import serializers

from apps.employers.models import Company
from apps.jobs.selectors import public_job_detail_queryset
from apps.jobs.serializers import PublicCompanyListSerializer, PublicJobListSerializer


class FavoriteJobCreateSerializer(serializers.Serializer):
    # Tin nháp, tin đã xóa, tin của công ty đã xóa coi như không tồn tại; tin đã đóng vẫn yêu thích được
    job_id = serializers.PrimaryKeyRelatedField(
        source='job',
        queryset=public_job_detail_queryset(),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Tin tuyển dụng không tồn tại.'},
    )


class FavoriteCompanyCreateSerializer(serializers.Serializer):
    company_id = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Company.objects.all(),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Công ty không tồn tại.'},
    )


class FavoriteJobSerializer(PublicJobListSerializer):
    """Một tin trong danh sách yêu thích: cùng cấu trúc với danh sách việc làm công khai + thời điểm thêm."""

    favorited_at = serializers.DateTimeField(read_only=True, help_text='Thời điểm thêm vào yêu thích')

    class Meta(PublicJobListSerializer.Meta):
        fields = PublicJobListSerializer.Meta.fields + ['favorited_at']


class FavoriteCompanySerializer(PublicCompanyListSerializer):
    favorited_at = serializers.DateTimeField(read_only=True, help_text='Thời điểm thêm vào yêu thích')

    class Meta(PublicCompanyListSerializer.Meta):
        fields = PublicCompanyListSerializer.Meta.fields + ['favorited_at']


class FavoriteIdsSerializer(serializers.Serializer):
    jobs = serializers.ListField(child=serializers.UUIDField(), help_text='Id các tin đang yêu thích')
    companies = serializers.ListField(child=serializers.UUIDField(), help_text='Id các công ty đang yêu thích')
