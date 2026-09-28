from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import HotelSetting, UserProfile, Room, Client, Reservation, Service, Expense, Payment
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Associe toutes les données existantes (sans hôtel) à un hôtel principal par défaut (pour le déploiement en production)'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- DÉBUT DE LA MIGRATION DES DONNÉES VERS LE MULTI-HÔTEL ---")
        
        with transaction.atomic():
            # 1. Créer ou récupérer un hôtel par défaut
            hotel, created = HotelSetting.objects.get_or_create(
                nom_etablissement="Hôtel Principal",
                defaults={
                    'adresse': "Adresse Principale",
                    'telephone': "+0000000000",
                    'email': "contact@hotel.com"
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"[*] Nouvel hôtel créé : {hotel.nom_etablissement}"))
            else:
                self.stdout.write(f"[*] Utilisation de l'hôtel existant : {hotel.nom_etablissement}")

            # 2. Associer les administrateurs et membres du staff existants à cet hôtel
            staff_users = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
            for user in staff_users.distinct():
                profile, p_created = UserProfile.objects.get_or_create(user=user)
                if not profile.hotel:
                    profile.hotel = hotel
                    profile.save()
                    self.stdout.write(f"  - Administrateur '{user.username}' associé à l'hôtel")

            # 3. Mettre à jour toutes les entités sans hôtel
            models_to_update = [
                (Room, 'Chambres'),
                (Client, 'Clients'),
                (Reservation, 'Réservations'),
                (Service, 'Services'),
                (Expense, 'Dépenses'),
                (Payment, 'Paiements')
            ]
            
            for Model, nom_pluriel in models_to_update:
                if hasattr(Model, 'hotel'):
                    updated = Model.objects.filter(hotel__isnull=True).update(hotel=hotel)
                    if updated > 0:
                        self.stdout.write(self.style.SUCCESS(f"  - {updated} {nom_pluriel} migrées vers l'hôtel principal."))
                    else:
                        self.stdout.write(f"  - 0 {nom_pluriel} à migrer.")

        self.stdout.write(self.style.SUCCESS("\n✅ MIGRATION RÉUSSIE AVEC SUCCÈS. Aucune donnée n'a été perdue !"))
