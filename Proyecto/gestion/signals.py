# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Almacen, User


@receiver(post_save, sender=User)
def crear_almacen(sender, instance, created, **kwargs):
    if created:
        Almacen.objects.create(propietario=instance, nombre=f"Almacen de {instance.username}")
