# Generated by Django 4.2.15 on 2025-03-10 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0032_blend_overhead_absorbed_transaction_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='production_report',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
