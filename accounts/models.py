from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        if not full_name:
            raise ValueError("Le nom complet est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMINISTRATEUR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Un superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Un superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    AGRICULTEUR = 'agriculteur'
    ADMINISTRATEUR = 'administrateur'
    ROLE_CHOICES = [
        (AGRICULTEUR, 'Agriculteur'),
        (ADMINISTRATEUR, 'Administrateur'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=AGRICULTEUR)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def is_administrateur(self):
        return self.role == self.ADMINISTRATEUR

    @property
    def is_agriculteur(self):
        return self.role == self.AGRICULTEUR
