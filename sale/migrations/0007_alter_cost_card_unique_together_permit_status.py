# Generated by Django 4.2.15 on 2025-03-25 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0006_cost_card_valid_from_cost_card_valid_till_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cost_card',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='permit',
            name='status',
            field=models.CharField(default='pending', max_length=50),
        ),
    ]
