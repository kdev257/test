# Generated by Django 4.2.15 on 2025-06-01 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0048_alter_lower_tds_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
