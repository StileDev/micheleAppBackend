from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from irrigation.models import Parcelle
from .permissions import IsAdminRole
from .serializers import (
    ManageUserSerializer,
    ManageUserCreateSerializer,
    ManageUserUpdateSerializer,
    AdminParcelleSerializer,
)

User = get_user_model()


# ---- Utilisateurs : CRUD complet ----

class UserListCreateView(generics.ListCreateAPIView):
    """GET  -> liste des utilisateurs (recherche via ?search=...)
    POST -> création d'un utilisateur par l'administrateur, rôle libre."""

    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        return ManageUserCreateSerializer if self.request.method == 'POST' else ManageUserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('full_name')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(email__icontains=search))
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(ManageUserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """GET, PATCH, DELETE sur un utilisateur précis."""

    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        return User.objects.filter(pk=pk).first()

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'Utilisateur introuvable.'}, status=404)
        return Response(ManageUserSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'Utilisateur introuvable.'}, status=404)

        serializer = ManageUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ManageUserSerializer(user).data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'Utilisateur introuvable.'}, status=404)
        if user.pk == request.user.pk:
            return Response({'detail': 'Vous ne pouvez pas supprimer votre propre compte.'}, status=400)

        # Suppression définitive du compte (CRUD complet demandé).
        # Ses tokens JWT existants deviendront invalides à leur expiration
        # naturelle ou au prochain refresh (l'utilisateur n'existant plus,
        # JWTAuthentication le rejettera).
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- Parcelles : vue d'ensemble ----

class AdminParcelleListView(generics.ListAPIView):
    """Liste de toutes les parcelles du système, tous agriculteurs
    confondus, avec le nom du propriétaire."""

    permission_classes = [IsAdminRole]
    serializer_class = AdminParcelleSerializer

    def get_queryset(self):
        queryset = Parcelle.objects.select_related('user').order_by('-created_at')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(nom__icontains=search) | Q(user__full_name__icontains=search))
        return queryset


class AdminParcelleDeleteView(APIView):
    permission_classes = [IsAdminRole]

    def delete(self, request, pk):
        parcelle = Parcelle.objects.filter(pk=pk).first()
        if not parcelle:
            return Response({'detail': 'Parcelle introuvable.'}, status=404)
        parcelle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
