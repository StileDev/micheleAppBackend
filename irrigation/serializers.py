from rest_framework import serializers
from .models import Parcelle, Materiel, Mesure, EtatParcelle, ActionLog


class ParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcelle
        fields = ['id', 'nom', 'superficie', 'culture', 'latitude', 'longitude', 'created_at', 'device_key']
        read_only_fields = ['id', 'created_at', 'device_key']


class MaterielSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materiel
        fields = ['id', 'nom', 'created_at']
        read_only_fields = ['id', 'created_at']


class EtatParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtatParcelle
        fields = ['iot_connecte', 'irrigation_mode', 'irrigation_active', 'irrigation_demarree_a']


class ParcelleDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    device_key = serializers.CharField()
    etat = EtatParcelleSerializer()
    temperature = serializers.FloatField(allow_null=True)
    humidite_air = serializers.FloatField(allow_null=True)
    humidite_sol = serializers.FloatField(allow_null=True)
    derniere_mesure = serializers.DateTimeField(allow_null=True)
    materiels = MaterielSerializer(many=True)


class MesureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesure
        fields = ['humidite_sol', 'temperature', 'humidite_air']


class MesureTempsReelSerializer(serializers.Serializer):
    humidite_sol = serializers.FloatField(required=False)
    temperature = serializers.FloatField(required=False)
    humidite_air = serializers.FloatField(required=False)


class MesureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesure
        fields = ['humidite_sol', 'temperature', 'humidite_air', 'created_at']


class ModeUpdateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=EtatParcelle.MODE_CHOICES)


class ActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionLog
        fields = ['id', 'statut', 'declenchee_automatiquement', 'created_at']


class HistoriqueSerializer(serializers.Serializer):
    actions = ActionLogSerializer(many=True)
    mesures = MesureSerializer(many=True)


class RaisonPrevisionSerializer(serializers.Serializer):
    titre = serializers.CharField()
    detail = serializers.CharField()


class PointPrevisionSerializer(serializers.Serializer):
    label = serializers.CharField()
    valeur = serializers.FloatField()


class PrevisionSerializer(serializers.Serializer):
    besoin_eau = serializers.BooleanField()
    message = serializers.CharField()
    raisons = RaisonPrevisionSerializer(many=True)
    courbe = PointPrevisionSerializer(many=True)


class PompeEtatSerializer(serializers.Serializer):
    irrigation_actif = serializers.BooleanField()