"""Đổi thang cấp bậc kiểu IT (Junior/Middle/Senior/Lead) sang thang dùng chung cho mọi ngành nghề."""
from django.conf import settings
from django.db import migrations, models

# Cấp bậc cũ -> mới. intern, fresher, manager giữ nguyên giá trị.
LEVEL_MAP = {'junior': 'staff', 'middle': 'staff', 'senior': 'staff', 'lead': 'supervisor'}
REVERSE_MAP = {'staff': 'junior', 'supervisor': 'lead', 'director': 'manager'}


def remap(mapping):
    def run(apps, schema_editor):
        Job = apps.get_model('jobs', 'Job')
        for old, new in mapping.items():
            Job._base_manager.filter(level=old).update(level=new)  # gồm cả tin đã xóa mềm

    return run


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_seed_catalog'),
        ('employers', '0001_initial'),
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='job',
            name='ck_jobs_level',
        ),
        migrations.RunPython(remap(LEVEL_MAP), remap(REVERSE_MAP)),
        migrations.AlterField(
            model_name='job',
            name='level',
            field=models.CharField(choices=[('intern', 'Thực tập sinh'), ('fresher', 'Mới tốt nghiệp'), ('staff', 'Nhân viên'), ('supervisor', 'Trưởng nhóm / Giám sát'), ('manager', 'Trưởng / Phó phòng'), ('director', 'Giám đốc / Cấp cao')], max_length=20, verbose_name='cấp bậc'),
        ),
        migrations.AddConstraint(
            model_name='job',
            constraint=models.CheckConstraint(condition=models.Q(('level__in', ['intern', 'fresher', 'staff', 'supervisor', 'manager', 'director'])), name='ck_jobs_level'),
        ),
    ]
