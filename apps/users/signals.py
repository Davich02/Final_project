from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User


@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        tenant_group, _ = Group.objects.get_or_create(name='Tenants')
        instance.groups.add(tenant_group)