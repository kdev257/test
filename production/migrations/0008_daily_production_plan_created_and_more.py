# Generated by Django 4.2.15 on 2025-01-28 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0010_brand_finished_blend_item_brand_finished_goods_item_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('production', '0007_delete_blend_requisition'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_production_plan',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='daily_production_plan',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_production_plan_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='daily_production_plan',
            name='modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='daily_production_plan',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_production_plan_unit', to='masters.unit'),
        ),
    ]
