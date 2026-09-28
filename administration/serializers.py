from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from irrigation.models import Parcelle

User = get_user_model()


class ManageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'role', 'is_active']


class ManageUserCreateSerializer(serializers.ModelSerializer):
    """Création d'un utilisateur par un administrateur — contrairement à
    l'inscription publique, le rôle est choisi librement ici."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'role', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ManageUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'role', 'is_active']


class AdminParcelleSerializer(serializers.ModelSerializer):
    """Vue d'ensemble d'une parcelle pour l'administrateur, avec le nom
    et l'email de son propriétaire."""

    proprietaire_nom = serializers.CharField(source='user.full_name', read_only=True)
    proprietaire_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Parcelle
        fields = ['id', 'nom', 'superficie', 'culture', 'proprietaire_nom', 'proprietaire_email', 'created_at']
