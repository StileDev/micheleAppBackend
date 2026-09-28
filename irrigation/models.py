import secrets
from django.db import models
from django.conf import settings


def generer_device_key():
    return secrets.token_hex(16)  # 32 caractères hexadécimaux, imprévisible


class Parcelle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parcelles')
    nom = models.CharField(max_length=100)
    superficie = models.FloatField(help_text="En hectares", null=True, blank=True)
    culture = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Clé propre à cette parcelle, utilisée UNIQUEMENT par le capteur IoT
    # (ESP32) pour envoyer ses mesures — indépendante du compte de
    # l'agriculteur, générée automatiquement, jamais un mot de passe humain.
    device_key = models.CharField(max_length=32, unique=True, editable=False, default=generer_device_key)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom} ({self.user.email})"


class Materiel(models.Model):
    """Capteur ou actionneur rattaché à une parcelle (ex: Capteur Humidité,
    ESP32, Capteur PIR...). Simple liste libre, comme dans l'écran
    'Gestion état parcelle et matériels'."""

    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='materiels')
    nom = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.nom} — {self.parcelle.nom}"


class Mesure(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='mesures')
    humidite_sol = models.FloatField(help_text="Pourcentage")
    temperature = models.FloatField(help_text="Degrés Celsius")
    humidite_air = models.FloatField(help_text="Pourcentage")
    ph_sol = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Mesure {self.parcelle.nom} @ {self.created_at:%d/%m %H:%M}"

class EtatParcelle(models.Model):
    AUTO = 'auto'
    MANUEL = 'manuel'
    MODE_CHOICES = [(AUTO, 'Automatique'), (MANUEL, 'Manuel')]

    parcelle = models.OneToOneField(Parcelle, on_delete=models.CASCADE, related_name='etat')
    iot_connecte = models.BooleanField(default=True)

    irrigation_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MANUEL)
    irrigation_active = models.BooleanField(default=False)
    irrigation_demarree_a = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"État {self.parcelle.nom}"

class ActionLog(models.Model):
    DEMARRAGE = 'demarrage'
    ARRET = 'arret'
    STATUT_CHOICES = [(DEMARRAGE, 'Démarrage'), (ARRET, 'Arrêt')]

    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='actions')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    declenchee_automatiquement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Irrigation — {self.get_statut_display()} ({self.parcelle.nom})"