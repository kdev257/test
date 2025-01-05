# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account_Chart

# @receiver(post_save, sender=Account_Chart)
# def update_parent_balances_signal(sender, instance, created, **kwargs):
#     print(f"Signal triggered for instance: {instance}, created: {created}")
#     instance.update_parent_balances()
