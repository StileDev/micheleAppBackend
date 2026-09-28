from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Crée un compte administrateur IrrigaSmart."

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help="Adresse email du compte")
        parser.add_argument('--name', required=True, help="Nom complet")
        parser.add_argument('--password', required=True, help="Mot de passe")
        parser.add_argument('--phone', default='', help="Numéro de téléphone (facultatif)")

    def handle(self, *args, **options):
        email = options['email']

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.ERROR(f"Un compte existe déjà avec l'email {email}."))
            return

        User.objects.create_superuser(
            email=email,
            full_name=options['name'],
            password=options['password'],
            phone=options['phone'],
        )
        self.stdout.write(self.style.SUCCESS(f"Administrateur créé : {email}"))
