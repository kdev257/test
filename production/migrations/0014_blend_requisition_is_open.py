# Generated by Django 4.2.15 on 2025-02-06 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0013_alter_blend_requisition_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='blend_requisition',
            name='is_open',
            field=models.BooleanField(default=False),
        ),
    ]
