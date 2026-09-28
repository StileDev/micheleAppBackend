from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Autorise uniquement les utilisateurs dont le champ `role` vaut
    'administrateur'. Suppose que ce champ existe sur ton modèle User
    (app accounts) — adapte le nom du champ ici si le tien est différent
    (ex: is_staff, is_admin...)."""

    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'administrateur'
        )
