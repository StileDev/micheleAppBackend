from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Représentation d'un utilisateur renvoyée au frontend.
    Le champ `role` est indispensable : c'est lui qui détermine si
    l'application mobile affiche l'espace agriculteur ou l'espace
    administrateur après connexion."""

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'role']
        read_only_fields = ['id', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # L'inscription publique crée toujours un agriculteur. Le rôle
        # administrateur ne peut être attribué que par un administrateur
        # existant ou via la commande `create_admin`.
        validated_data['role'] = User.AGRICULTEUR
        return User.objects.create_user(**validated_data)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'phone']


class LoginSerializer(TokenObtainPairSerializer):
    """Ajoute les informations de l'utilisateur directement dans la réponse
    de connexion, ce qui évite au frontend un second appel à /me/."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
