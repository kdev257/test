# Generated by Django 4.2.15 on 2025-01-22 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0005_alter_gst_on_goods_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brand',
            old_name='wip_finished_blend',
            new_name='finished_blend',
        ),
    ]
