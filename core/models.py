from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import re

class Room(models.Model):
    hotel = models.ForeignKey(
        'HotelSetting',
        on_delete=models.CASCADE,
        related_name='rooms',
        null=True,
        blank=True,
        verbose_name="Hôtel"
    )
    # Choix des types de chambres
    TYPE_CHOICES = [
        ('Simple', 'Simple'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
        ('Dortoir', 'Dortoir'),
    ]

    # Choix des statuts
    STATUS_CHOICES = [
        ('Libre', 'Libre'),
        ('Occupée', 'Occupée'),
        ('En maintenance', 'En maintenance'),
        ('Hors service', 'Hors service'),
    ]

    numero_chambre = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="N° de Chambre"
    )

    type_chambre = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Simple'
    )

    prix_nuit = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Prix par nuit (FCFA)",
        default=0
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Équipements (Ex: Clim, Wi-Fi, Balcon...)"
    )

    statut_actuel = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Libre'
    )

    class Meta:
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"
        ordering = ['numero_chambre']

    def __str__(self):
        return f"Chambre {self.numero_chambre} ({self.type_chambre})"

    @property
    def est_disponible(self):
        """Vérifie si la chambre peut être louée immédiatement"""
        return self.statut_actuel == 'Libre'

    def mettre_a_jour_statut(self):
        """
        Vérifie si une réservation est en cours aujourd'hui pour
        ajuster le statut automatiquement.
        """
        today = timezone.now().date()
        res_active = self.reservations.filter(
            date_arrivee__lte=today,
            date_depart__gte=today,
            statut_reser__in=['Confirmée', 'En cours']
        ).exists()

        if res_active:
            self.statut_actuel = 'Occupée'
        elif self.statut_actuel == 'Occupée':
            self.statut_actuel = 'Libre'

        self.save(update_fields=['statut_actuel'])


def validate_numero_cni(value):
    """
    CNI Côte d'Ivoire (ONECI biométrique) :
    - Nouveau format NNI  : C + 9 chiffres  → ex: C123456789
    - Ancien format       : CI + 7 à 10 chiffres → ex: CI1234567
    """
    pattern = r'^(C\d{9}|CI\d{7,10})$'
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            "Numéro CNI invalide. "
            "Format attendu : C123456789 (NNI) ou CI1234567 (ancienne CNI)."
        )


def validate_numero_passeport(value):
    """
    Passeport Côte d'Ivoire :
    - 2 lettres + 7 chiffres → ex: CI1234567 ou AB1234567
    """
    pattern = r'^[A-Z]{2}\d{7}$'
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            "Numéro de passeport invalide. "
            "Format attendu : 2 lettres + 7 chiffres (ex: CI1234567)."
        )


class Client(models.Model):
    hotel = models.ForeignKey(
        'HotelSetting',
        on_delete=models.CASCADE,
        related_name='clients',
        null=True,
        blank=True,
        verbose_name="Hôtel"
    )
    TYPE_DOCUMENT = [
        ('CNI', 'Carte Nationale d\'Identité'),
        ('Passeport', 'Passeport'),
    ]

    # Numéro séquentiel propre à chaque hôtel (affiché #00001), attribué à la création
    numero_client = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="N° client"
    )
    date_creation = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Client depuis"
    )

    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=50, blank=True)

    type_document = models.CharField(max_length=20, choices=TYPE_DOCUMENT)
    numero_document = models.CharField(max_length=50)
 
    date_entree = models.DateField()
    date_sortie = models.DateField()

    def clean(self):
        """Validation du numéro selon le type de document choisi."""
        super().clean()
        if self.numero_document:
            numero = self.numero_document.upper().strip()
            if self.type_document == 'CNI':
                validate_numero_cni(numero)
            elif self.type_document == 'Passeport':
                validate_numero_passeport(numero)

        if self.date_entree and self.date_sortie:
            if self.date_sortie <= self.date_entree:
                raise ValidationError({
                    'date_sortie': "La date de sortie doit être postérieure à la date d'entrée."
                })

    def save(self, *args, **kwargs):
        # Normalise le numéro en majuscules avant sauvegarde
        if self.numero_document:
            self.numero_document = self.numero_document.upper().strip()
        if self.numero_client is None:
            dernier = Client.objects.filter(hotel=self.hotel).aggregate(
                m=models.Max('numero_client')
            )['m'] or 0
            self.numero_client = dernier + 1
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def code_client(self):
        """Numéro client formaté, ex : #00001"""
        if self.numero_client is None:
            return "—"
        return f"#{self.numero_client:05d}"

    @property
    def statut_sejour(self):
        """'Actif' pendant le séjour, 'À venir' avant, 'Parti' après."""
        today = timezone.localdate()
        if self.date_entree and today < self.date_entree:
            return 'À venir'
        if self.date_sortie and today > self.date_sortie:
            return 'Parti'
        return 'Actif'

    @property
    def nb_nuits(self):
        """Durée du séjour déclaré, en nuits (affichage)."""
        if self.date_entree and self.date_sortie:
            return max((self.date_sortie - self.date_entree).days, 0)
        return 0

    @property
    def initiales(self):
        return f"{self.prenom[:1]}{self.nom[:1]}".upper()

    def __str__(self):
        return f"{self.code_client} - {self.prenom} {self.nom}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['numero_client']
        constraints = [
            models.UniqueConstraint(
                fields=['hotel', 'numero_client'],
                name='unique_numero_client_par_hotel'
            ),
        ]


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Confirmée', 'Confirmée'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Annulée', 'Annulée'),
    ]

    client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    chambre = models.ForeignKey(
        'Room', 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    
    # Prix de la nuit au moment de la réservation
    prix_nuit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Prix par nuit (copié depuis la chambre)"
    )
    
    # Avance versée
    montant_avance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    statut_reser = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Confirmée'
    )

    class Meta:
        ordering = ['-date_reservation']
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"Rés. #{self.id} - {self.client.prenom} {self.client.nom} - Ch.{self.chambre.numero_chambre}"

    def clean(self):
        """Validation des dates et disponibilité"""
        super().clean()
        
        # Vérifier que date_depart > date_arrivee
        if self.date_depart and self.date_arrivee:
            if self.date_depart <= self.date_arrivee:
                raise ValidationError({
                    'date_depart': "La date de départ doit être postérieure à la date d'arrivée."
                })
        
        # Vérifier les chevauchements (chambre_id : la chambre peut être absente ou refusée)
        if self.chambre_id and self.date_arrivee and self.date_depart:
            overlapping = Reservation.objects.filter(
                chambre_id=self.chambre_id,
                statut_reser__in=['Confirmée', 'En cours']
            ).exclude(pk=self.pk).filter(
                date_arrivee__lt=self.date_depart,
                date_depart__gt=self.date_arrivee
            )
            
            if overlapping.exists():
                raise ValidationError({
                    'chambre': f"Cette chambre est déjà réservée du {overlapping.first().date_arrivee} au {overlapping.first().date_depart}."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def nb_nuits(self):
        """Nombre de nuits du séjour"""
        if self.date_depart and self.date_arrivee:
            return (self.date_depart - self.date_arrivee).days
        return 0

    @property
    def total_chambre(self):
        """Montant total des nuitées"""
        return self.nb_nuits * self.prix_nuit

    @property
    def total_services(self):
        """Total des services additionnels"""
        agg = self.services.aggregate(total=models.Sum('prix_service'))
        return agg['total'] or 0

    @property
    def total_paye(self):
        """Total des paiements effectués"""
        agg = self.paiements.aggregate(total=models.Sum('montant_paye'))
        return agg['total'] or 0

    @property
    def solde_du(self):
        """Solde restant à payer"""
        total_facture = self.total_chambre + self.total_services
        return total_facture - self.total_paye

    @property
    def est_entierement_paye(self):
        """Vérifie si la réservation est entièrement payée"""
        return self.solde_du <= 0

    @property
    def pourcentage_paye(self):
        """Pourcentage du montant total qui a été payé"""
        total_facture = self.total_chambre + self.total_services
        if total_facture > 0:
            return round((self.total_paye / total_facture) * 100, 1)
        return 0


class Service(models.Model):
    # Décommenté pour que la Reservation puisse compter ses services
    # Hôtel propriétaire : un service créé dans la page Services (sans réservation)
    # n'est proposé qu'aux réservations de cet hôtel
    hotel = models.ForeignKey(
        'HotelSetting',
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
        blank=True,
        verbose_name="Hôtel"
    )
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='services', null=True)
    nom_service = models.CharField(max_length=100)
    prix_service = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.hotel_id and self.reservation_id:
            self.hotel = self.reservation.chambre.hotel
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_service}"

# --- PAYEMENTS ---
class Payment(models.Model):
    METHOD_CHOICES = [
        ('Espèces', 'Espèces'),
        ('Mobile Money', 'Mobile Money'),
        ('Carte Bancaire', 'Carte Bancaire'),
    ]

    # Relation vers la réservation (Un paiement appartient à une réservation)
    reservation = models.ForeignKey(
        'Reservation', 
        on_delete=models.CASCADE, 
        related_name='paiements'
    )
    
    montant_paye = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Montant versé par le client"
    )
    
    date_paiement = models.DateTimeField(auto_now_add=True)
    
    methode_paiement = models.CharField(
        max_length=20, 
        choices=METHOD_CHOICES
    )
    
    reference_paiement = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="ID transaction Mobile Money ou n° de reçu"
    )

    def __str__(self):
        return f"Paiement {self.id} - {self.reservation.client.nom} ({self.montant_paye} {self.reservation.client.devise if hasattr(self.reservation.client, 'devise') else 'FCFA'})"

    def clean(self):
        """Empêche de payer plus que ce qui est dû."""
        from django.core.exceptions import ValidationError
        
        # On vérifie si la réservation est définie pour éviter RelatedObjectDoesNotExist
        try:
            if self.reservation and self.montant_paye:
                if self.montant_paye > self.reservation.solde_du:
                    raise ValidationError(
                        f"Le montant ne peut pas dépasser le solde dû ({self.reservation.solde_du} FCFA)."
                    )
        except (Reservation.DoesNotExist, AttributeError):
            # Si la réservation n'est pas encore liée, on ne peut pas valider le solde
            pass

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
        


class Expense(models.Model):
    hotel = models.ForeignKey(
        'HotelSetting',
        on_delete=models.CASCADE,
        related_name='expenses',
        null=True,
        blank=True,
        verbose_name="Hôtel"
    )
    CATEGORIES = [
        ('Toute', 'Toute'),
        ('Entretien', 'Entretien'),
        ('Electricite', 'Electricite'),
        ('Eau', 'Eau'),
        ('Internet', 'Internet'),
        ('Maintenance', 'Maintenance'),
        ('Canal Plus', 'Canal Plus'),
        ('Frais bancaire', 'Frais bancaire'),
        ('Frais Wave', 'Frais Wave'),
        ('Investissement', 'Investissement'),
        ('Salaire', 'Salaire'),
        ('Autres', 'Autres'),
    ]
    # On enlève choices=CATEGORIES ici pour permettre des catégories personnalisées,
    # la validation se fera au niveau du formulaire.
    categorie = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField()
    justificatif = models.FileField(
        upload_to='justificatifs/',
        blank=True, null=True,
        verbose_name="Reçu (image ou PDF)",
        help_text="Formats acceptés : JPG, PNG, PDF"
    )

    def __str__(self):
        return f"{self.categorie} - {self.montant}"


def _update_room_status_on_reservation(reservation: Reservation):
    today = timezone.now().date()
    room = reservation.chambre
    
    if not room:
        return

    # CORRECTION : 'Terminée' au lieu de 'Terminé' pour correspondre à ton modèle
    if reservation.statut_reser == 'Terminée':
        room.statut_actuel = 'Libre'
        room.save(update_fields=['statut_actuel'])
    
    # Ajout du cas 'En cours' pour plus de sécurité
    elif reservation.statut_reser == 'En cours':
        room.statut_actuel = 'Occupée'
        room.save(update_fields=['statut_actuel'])

    elif reservation.statut_reser == 'Confirmée':
        if reservation.date_arrivee <= today <= reservation.date_depart:
            room.statut_actuel = 'Occupée'
            room.save(update_fields=['statut_actuel'])



@receiver(post_save, sender=Reservation)
def reservation_status_signal(sender, instance: Reservation, created, **kwargs):
    _update_room_status_on_reservation(instance)


class Report(models.Model):
    hotel = models.ForeignKey(
        'HotelSetting',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True,
        verbose_name="Hôtel"
    )
    date_debut = models.DateField()
    date_fin = models.DateField()
    type_report = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='rapports/')

    def __str__(self):
        return f"{self.type_report} - {self.date_debut} à {self.date_fin}"
        
    def clean(self):
        if self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
        
        
class HotelSetting(models.Model):
    # Informations générales
    nom_etablissement = models.CharField(max_length=255, default="Mon Hôtel")
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    nom_gerant = models.CharField(max_length=100, blank=True)
    devise = models.CharField(max_length=10, default="FCFA")

    # Informations fiscales et bancaires
    ifu = models.CharField(max_length=50, blank=True, verbose_name="IFU (Identifiant Fiscal Unique)")
    rccm = models.CharField(max_length=50, blank=True, verbose_name="RCCM")
    numero_compte_bancaire = models.CharField(max_length=60, blank=True, verbose_name="Numéro de compte bancaire")

    # Logo
    logo = models.ImageField(upload_to='logo/', blank=True, null=True)

    def __str__(self):
        return self.nom_etablissement

    class Meta:
        verbose_name = "Hôtel / Paramètre"
        verbose_name_plural = "Hôtels / Paramètres"


class UserProfile(models.Model):
    """Lie chaque utilisateur Django à un hôtel."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    hotel = models.ForeignKey(
        HotelSetting,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name="Hôtel"
    )

    def __str__(self):
        return f"{self.user.username} → {self.hotel.nom_etablissement}"

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"


class CalendarEvent(models.Model):
    """Événement du calendrier (comme dans la démo) : un client, une chambre, une date et un statut."""
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    hotel = models.ForeignKey(
        HotelSetting, on_delete=models.CASCADE, related_name='evenements',
        null=True, blank=True, verbose_name="Hôtel"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='evenements', verbose_name="Client")
    chambre = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='evenements', verbose_name="Chambre")
    date = models.DateField(verbose_name="Date")
    heure = models.TimeField(null=True, blank=True, verbose_name="Heure")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmee', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Événement du calendrier"
        verbose_name_plural = "Événements du calendrier"
        ordering = ['date', 'heure', 'id']

    def __str__(self):
        return f"{self.client} — Chambre {self.chambre.numero_chambre} le {self.date:%d/%m/%Y}"
