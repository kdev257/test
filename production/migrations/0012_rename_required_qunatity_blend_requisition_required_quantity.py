# Generated by Django 4.2.15 on 2025-02-04 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0011_blend_requisition_item_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blend_requisition',
            old_name='required_qunatity',
            new_name='required_quantity',
        ),
    ]
