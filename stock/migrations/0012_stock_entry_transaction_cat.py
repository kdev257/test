# Generated by Django 4.2.15 on 2025-02-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_alter_bom_items_bom_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_entry',
            name='transaction_cat',
            field=models.CharField(choices=[('Receipt', 'Receipt'), ('Issue', 'Issue')], default='Receipt', max_length=20),
        ),
    ]
