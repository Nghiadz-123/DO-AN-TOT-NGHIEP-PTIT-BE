import uuid

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_job_level_all_industries'),
        ('cvs', '0002_cv_parse_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='CVBuilderDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='ngày cập nhật')),
                ('content', models.JSONField(default=dict, verbose_name='nội dung CV')),
                ('candidate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cv_builder_document', to='candidates.candidateprofile', verbose_name='ứng viên')),
            ],
            options={
                'verbose_name': 'nội dung CV tự tạo',
                'verbose_name_plural': 'nội dung CV tự tạo',
                'db_table': 'cv_builder_documents',
            },
        ),
    ]
