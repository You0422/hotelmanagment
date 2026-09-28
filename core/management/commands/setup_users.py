"""Crée les groupes et, au besoin, un compte de départ.

Les mots de passe ne sont jamais écrits dans le code : ils sont donnés au lancement.

    python manage.py setup_users                      # crée seulement les groupes
    python manage.py setup_users --admin patron       # crée l'administrateur « patron »
    python manage.py setup_users --gerant marie       # crée le gérant « marie »

Le mot de passe est demandé à l'écran, ou lu dans la variable d'environnement
DJANGO_SETUP_PASSWORD (utile pour un script d'installation).
"""
import getpass
import os

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crée les groupes Admin et Gerant, et éventuellement un compte"

    def add_arguments(self, parser):
        parser.add_argument('--admin', metavar='NOM', help="Crée un administrateur (superutilisateur)")
        parser.add_argument('--gerant', metavar='NOM', help="Crée un gérant")

    def _mot_de_passe(self, username):
        mdp = os.environ.get('DJANGO_SETUP_PASSWORD')
        if not mdp:
            mdp = getpass.getpass(f"Mot de passe pour « {username} » : ")
            if mdp != getpass.getpass("Confirmation : "):
                raise CommandError("Les deux mots de passe ne correspondent pas.")
        try:
            validate_password(mdp, User(username=username))
        except ValidationError as e:
            raise CommandError("Mot de passe refusé : " + " ".join(e.messages))
        return mdp

    def _creer(self, username, groupe, superuser):
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError(f"Le compte « {username} » existe déjà. "
                               f"Changez son mot de passe avec : python manage.py changepassword {username}")
        user = User.objects.create_user(username=username, password=self._mot_de_passe(username))
        user.is_staff = user.is_superuser = superuser
        user.save()
        user.groups.add(Group.objects.get(name=groupe))
        self.stdout.write(self.style.SUCCESS(f"Compte « {username} » créé dans le groupe {groupe}."))
        self.stdout.write("Pensez à lui rattacher un hôtel (page Paramètres ou administration Django).")

    def handle(self, *args, **options):
        for name in ('Gerant', 'Admin'):
            _, cree = Group.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f'Groupe « {name} » créé') if cree else f'Groupe « {name} » existe déjà')

        if options['admin']:
            self._creer(options['admin'], 'Admin', superuser=True)
        if options['gerant']:
            self._creer(options['gerant'], 'Gerant', superuser=False)
        if not options['admin'] and not options['gerant']:
            self.stdout.write("\nAucun compte demandé. Exemple : python manage.py setup_users --admin patron")
