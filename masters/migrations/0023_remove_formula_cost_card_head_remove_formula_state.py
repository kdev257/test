# Generated by Django 4.2.15 on 2025-03-20 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0022_alter_formula_cost_card_head'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formula',
            name='cost_card_head',
        ),
        migrations.RemoveField(
            model_name='formula',
            name='state',
        ),
    ]
