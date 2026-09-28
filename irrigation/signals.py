from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Parcelle, EtatParcelle


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_parcelle(sender, instance, created, **kwargs):
    """Chaque nouvel agriculteur reçoit une première parcelle, pour que
    l'écran 'Mes parcelles' ne soit jamais vide au premier lancement.
    L'utilisateur peut ensuite en ajouter d'autres depuis l'app."""
    if created and getattr(instance, 'role', 'agriculteur') != 'administrateur':
        Parcelle.objects.create(user=instance, nom="Ma première parcelle")


@receiver(post_save, sender=Parcelle)
def create_etat_parcelle(sender, instance, created, **kwargs):
    if created:
        EtatParcelle.objects.get_or_create(parcelle=instance)
