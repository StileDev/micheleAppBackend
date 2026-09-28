from django.shortcuts import get_object_or_404
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Parcelle, Materiel, EtatParcelle, ActionLog, Mesure
from .serializers import (
    ParcelleSerializer,
    MaterielSerializer,
    MesureCreateSerializer,
    MesureTempsReelSerializer,
    MesureSerializer,
    ParcelleDetailSerializer,
    HistoriqueSerializer,
    PrevisionSerializer,
    ModeUpdateSerializer,
    EtatParcelleSerializer,
    PompeEtatSerializer,
)
from .services import calculer_prevision, decider_irrigation_auto


def diffuser_mesure(parcelle, mesure):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        **MesureSerializer(mesure).data,
        'etat': EtatParcelleSerializer(parcelle.etat).data,
    }
    async_to_sync(channel_layer.group_send)(
        f'parcelle_{parcelle.id}',
        {'type': 'mesure.update', 'payload': payload},
    )


def appliquer_decision_auto(parcelle, mesure):
    etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)

    if etat.irrigation_mode != EtatParcelle.AUTO:
        return etat

    doit_tourner = decider_irrigation_auto(mesure.humidite_sol, etat.irrigation_active)

    if doit_tourner != etat.irrigation_active:
        etat.irrigation_active = doit_tourner
        etat.irrigation_demarree_a = timezone.now() if doit_tourner else None
        etat.save()
        ActionLog.objects.create(
            parcelle=parcelle,
            statut=ActionLog.DEMARRAGE if doit_tourner else ActionLog.ARRET,
            declenchee_automatiquement=True,
        )

    return etat


def get_parcelle_du_user(request, parcelle_id):
    return get_object_or_404(Parcelle, id=parcelle_id, user=request.user)


def get_parcelle_par_device_key(request, parcelle_id):
    device_key = request.headers.get('X-Device-Key')
    if not device_key:
        return None
    return Parcelle.objects.filter(id=parcelle_id, device_key=device_key).first()


class ParcelleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ParcelleSerializer

    def get_queryset(self):
        return Parcelle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ParcelleDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        parcelle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParcelleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)
        derniere_mesure = parcelle.mesures.first()

        data = {
            'id': parcelle.id,
            'nom': parcelle.nom,
            'device_key': parcelle.device_key,
            'etat': etat,
            'temperature': derniere_mesure.temperature if derniere_mesure else None,
            'humidite_air': derniere_mesure.humidite_air if derniere_mesure else None,
            'humidite_sol': derniere_mesure.humidite_sol if derniere_mesure else None,
            'derniere_mesure': derniere_mesure.created_at if derniere_mesure else None,
            'materiels': parcelle.materiels.all(),
        }
        return Response(ParcelleDetailSerializer(data).data)


class MaterielListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterielSerializer

    def get_queryset(self):
        parcelle = get_parcelle_du_user(self.request, self.kwargs['parcelle_id'])
        return parcelle.materiels.all()

    def perform_create(self, serializer):
        parcelle = get_parcelle_du_user(self.request, self.kwargs['parcelle_id'])
        serializer.save(parcelle=parcelle)


class MaterielDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, parcelle_id, materiel_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        materiel = get_object_or_404(Materiel, id=materiel_id, parcelle=parcelle)
        materiel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MesureCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = MesureCreateSerializer

    def create(self, request, *args, **kwargs):
        parcelle = get_parcelle_par_device_key(request, self.kwargs['parcelle_id'])
        if parcelle is None:
            return Response({'detail': "Clé d'appareil invalide ou manquante (header X-Device-Key)."}, status=401)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mesure = serializer.save(parcelle=parcelle)

        appliquer_decision_auto(parcelle, mesure)
        diffuser_mesure(parcelle, mesure)

        return Response(MesureSerializer(mesure).data, status=status.HTTP_201_CREATED)


class MesureTempsReelUpdateView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, parcelle_id):
        parcelle = get_parcelle_par_device_key(request, parcelle_id)
        if parcelle is None:
            return Response({'detail': "Clé d'appareil invalide ou manquante (header X-Device-Key)."}, status=401)

        serializer = MesureTempsReelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        if not payload:
            return Response({'detail': 'Envoyez au moins un champ à mettre à jour.'}, status=400)

        derniere = parcelle.mesures.first()

        mesure = Mesure.objects.create(
            parcelle=parcelle,
            humidite_sol=payload.get('humidite_sol', derniere.humidite_sol if derniere else 0),
            temperature=payload.get('temperature', derniere.temperature if derniere else 0),
            humidite_air=payload.get('humidite_air', derniere.humidite_air if derniere else 0),
        )

        appliquer_decision_auto(parcelle, mesure)
        diffuser_mesure(parcelle, mesure)

        return Response(MesureSerializer(mesure).data, status=status.HTTP_200_OK)


class PompeEtatView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, parcelle_id):
        parcelle = get_parcelle_par_device_key(request, parcelle_id)
        if parcelle is None:
            return Response({'detail': "Clé d'appareil invalide ou manquante (header X-Device-Key)."}, status=401)

        etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)
        return Response(PompeEtatSerializer({'irrigation_actif': etat.irrigation_active}).data)


class DemarrerIrrigationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)

        if etat.irrigation_mode != EtatParcelle.MANUEL:
            return Response({'detail': "Passez d'abord en mode manuel pour déclencher l'irrigation vous-même."}, status=400)

        etat.irrigation_active = True
        etat.irrigation_demarree_a = timezone.now()
        etat.save()
        ActionLog.objects.create(parcelle=parcelle, statut=ActionLog.DEMARRAGE)
        return Response({'etat': 'irrigation démarrée'}, status=200)


class ArreterIrrigationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)
        etat.irrigation_active = False
        etat.irrigation_demarree_a = None
        etat.save()
        ActionLog.objects.create(parcelle=parcelle, statut=ActionLog.ARRET)
        return Response({'etat': 'irrigation arrêtée'}, status=200)


class IrrigationModeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcelle_id):
        serializer = ModeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parcelle = get_parcelle_du_user(request, parcelle_id)
        etat, _ = EtatParcelle.objects.get_or_create(parcelle=parcelle)
        etat.irrigation_mode = serializer.validated_data['mode']
        etat.irrigation_active = False
        etat.irrigation_demarree_a = None
        etat.save()

        return Response({'irrigation_mode': etat.irrigation_mode})


class HistoriqueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        data = {
            'actions': parcelle.actions.all()[:50],
            'mesures': parcelle.mesures.all()[:30],
        }
        return Response(HistoriqueSerializer(data).data)


class PrevisionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcelle_id):
        parcelle = get_parcelle_du_user(request, parcelle_id)
        derniere_mesure = parcelle.mesures.first()
        data = calculer_prevision(derniere_mesure)
        return Response(PrevisionSerializer(data).data)