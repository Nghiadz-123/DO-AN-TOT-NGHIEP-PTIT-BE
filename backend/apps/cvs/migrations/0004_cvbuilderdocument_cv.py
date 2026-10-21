from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cvs', '0003_cv_builder_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvbuilderdocument',
            name='cv',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='builder_document', to='cvs.cv', verbose_name='CV'),
        ),
    ]
