# Generated by Django 4.2.15 on 2025-01-09 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0004_alter_user_roles_department'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gst_on_goods',
            options={'verbose_name_plural': 'GST On Goods'},
        ),
        migrations.AddIndex(
            model_name='gst_on_goods',
            index=models.Index(fields=['item'], name='masters_gst_item_id_4b9792_idx'),
        ),
    ]
