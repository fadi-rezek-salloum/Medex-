from company.models import Company
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def create_company_from_user(sender, instance, created, **kwargs):
    if created and instance.is_supplier:
        with transaction.atomic():
            company_instance, _ = Company.objects.get_or_create(
                supplier=instance,
                defaults={
                    "name": instance.full_name,
                    "email": instance.email,
                    "phone": instance.phone,
                    "address": instance.shipping_address,
                },
            )
