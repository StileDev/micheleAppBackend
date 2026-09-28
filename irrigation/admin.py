from django.contrib import admin
from .models import Parcelle, Materiel, Mesure, EtatParcelle, ActionLog


@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'user', 'superficie', 'culture', 'device_key', 'created_at']
    search_fields = ['nom', 'user__email', 'device_key']
    readonly_fields = ['device_key']


@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ['nom', 'parcelle', 'created_at']
    list_filter = ['parcelle']


@admin.register(Mesure)
class MesureAdmin(admin.ModelAdmin):
    list_display = ['parcelle', 'humidite_sol', 'temperature', 'humidite_air', 'created_at']
    list_filter = ['parcelle']
    ordering = ['-created_at']


@admin.register(EtatParcelle)
class EtatParcelleAdmin(admin.ModelAdmin):
    list_display = ['parcelle', 'iot_connecte', 'irrigation_mode', 'irrigation_active']


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['parcelle', 'statut', 'declenchee_automatiquement', 'created_at']
    list_filter = ['statut', 'declenchee_automatiquement']
    ordering = ['-created_at']