"""Données d'exemple d'un hôtel (même contenu que le bouton « Ajouter des données d'exemple » de la démo)."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Client, Expense, Payment, Reservation, Room, Service


def add_sample_data(hotel):
    """Ajoute chambres, clients, réservations, services, paiement et dépenses d'exemple à `hotel`.

    Ne touche pas aux données existantes. Retourne False si les exemples sont déjà présents.
    Les numéros de chambre sont préfixés par l'identifiant de l'hôtel (ex. 101, 102… pour l'hôtel 1)
    car un numéro de chambre est unique dans toute la base.
    """
    prefix = str(hotel.pk)
    numeros = [f"{prefix}01", f"{prefix}02", f"{prefix}03", f"{prefix}04"]
    if Room.objects.filter(numero_chambre__in=numeros).exists():
        return False

    today = timezone.localdate()
    with transaction.atomic():
        chambres = [
            Room.objects.create(hotel=hotel, numero_chambre=numeros[0], type_chambre='Simple', prix_nuit=15000,
                                statut_actuel='Libre', description="Chambre simple avec vue sur jardin"),
            Room.objects.create(hotel=hotel, numero_chambre=numeros[1], type_chambre='Double', prix_nuit=25000,
                                statut_actuel='Libre', description="Chambre double confortable"),
            Room.objects.create(hotel=hotel, numero_chambre=numeros[2], type_chambre='Suite', prix_nuit=50000,
                                statut_actuel='Libre', description="Suite luxueuse avec balcon"),
            Room.objects.create(hotel=hotel, numero_chambre=numeros[3], type_chambre='Double', prix_nuit=25000,
                                statut_actuel='Libre', description="Chambre double avec climatisation"),
        ]

        jean = Client.objects.create(
            hotel=hotel, nom="Kouadio", prenom="Jean", telephone="+225 07 12 34 56",
            email=f"jean.kouadio.h{hotel.pk}@exemple.ci", adresse="Cocody, Abidjan",
            type_document='CNI', numero_document=f"C{hotel.pk:03d}123456",
            date_entree=today, date_sortie=today + timedelta(days=3),
        )
        fatou = Client.objects.create(
            hotel=hotel, nom="Diallo", prenom="Fatou", telephone="+225 05 78 90 12",
            email=f"fatou.diallo.h{hotel.pk}@exemple.ci", adresse="Yopougon, Abidjan",
            type_document='Passeport', numero_document=f"AB{hotel.pk:02d}12345",
            date_entree=today + timedelta(days=5), date_sortie=today + timedelta(days=8),
        )

        # Séjour en cours (comme la démo) + une réservation à venir
        sejour = Reservation.objects.create(
            client=jean, chambre=chambres[3], date_arrivee=today, date_depart=today + timedelta(days=3),
            prix_nuit=chambres[3].prix_nuit, statut_reser='En cours',
        )
        Reservation.objects.create(
            client=fatou, chambre=chambres[2], date_arrivee=today + timedelta(days=5),
            date_depart=today + timedelta(days=8), prix_nuit=chambres[2].prix_nuit, statut_reser='Confirmée',
        )

        for nom, prix, description in [("Petit-déjeuner", 2000, "Petit-déjeuner continental"),
                                       ("Blanchisserie", 1500, "Service de blanchisserie"),
                                       ("Transfert aéroport", 10000, "Navette vers l'aéroport")]:
            Service.objects.create(reservation=sejour, nom_service=nom, prix_service=prix, description=description)

        Payment.objects.create(reservation=sejour, montant_paye=50000, methode_paiement='Espèces')

        Expense.objects.create(hotel=hotel, categorie='Electricite', montant=45000,
                               description="Facture d'électricité du mois", date_depense=today)
        Expense.objects.create(hotel=hotel, categorie='Entretien', montant=15000,
                               description="Produits de nettoyage", date_depense=today)
    return True
