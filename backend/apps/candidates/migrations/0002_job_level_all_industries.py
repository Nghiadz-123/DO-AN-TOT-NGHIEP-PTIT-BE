"""Đổi cấp bậc hiện tại của ứng viên sang thang dùng chung cho mọi ngành (xem jobs.0002)."""
from django.db import migrations, models

LEVEL_MAP = {'junior': 'staff', 'middle': 'staff', 'senior': 'staff', 'lead': 'supervisor'}
REVERSE_MAP = {'staff': 'junior', 'supervisor': 'lead', 'director': 'manager'}


def remap(mapping):
    def run(apps, schema_editor):
        CandidateProfile = apps.get_model('candidates', 'CandidateProfile')
        for old, new in mapping.items():
            CandidateProfile._base_manager.filter(current_level=old).update(current_level=new)

    return run


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remap(LEVEL_MAP), remap(REVERSE_MAP)),
        migrations.AlterField(
            model_name='candidateprofile',
            name='current_level',
            field=models.CharField(blank=True, choices=[('intern', 'Thực tập sinh'), ('fresher', 'Mới tốt nghiệp'), ('staff', 'Nhân viên'), ('supervisor', 'Trưởng nhóm / Giám sát'), ('manager', 'Trưởng / Phó phòng'), ('director', 'Giám đốc / Cấp cao')], max_length=20, verbose_name='cấp bậc hiện tại'),
        ),
    ]
