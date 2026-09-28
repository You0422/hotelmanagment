from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Room, Client, Reservation, Service, Payment, Expense, Report, HotelSetting, UserProfile


# --- Inline pour lier un profil (hôtel) à un utilisateur ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Profil hôtel"
    verbose_name_plural = "Profil hôtel"

# Étendre l'admin User pour inclure le profil
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

# Désinscrire le User par défaut, réinscrire avec le profil
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# --- HotelSetting (gestion des hôtels via admin) ---
@admin.register(HotelSetting)
class HotelSettingAdmin(admin.ModelAdmin):
    list_display = ('nom_etablissement', 'telephone', 'email', 'devise')
    search_fields = ('nom_etablissement',)


# --- Modèles existants (inchangés, avec hotel ajouté) ---
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('numero_chambre', 'type_chambre', 'statut_actuel', 'hotel')
    list_filter = ('type_chambre', 'statut_actuel', 'hotel')
    search_fields = ('numero_chambre',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone', 'hotel')
    list_filter = ('hotel',)
    search_fields = ('nom', 'prenom', 'email', 'telephone')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'chambre', 'date_arrivee', 'date_depart', 'statut_reser', 'get_solde')
    list_filter = ('statut_reser', 'date_arrivee', 'chambre')
    search_fields = ('client__nom', 'chambre__numero_chambre')
    inlines = [PaymentInline]
    readonly_fields = ('date_reservation',)
    
    def get_solde(self, obj):
        try:
            return f"{obj.solde_du} FCFA"
        except:
            return "N/A"
    get_solde.short_description = 'Solde restant'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nom_service', 'prix_service')
    search_fields = ('nom_service',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'montant_paye', 'methode_paiement', 'date_paiement')
    list_filter = ('methode_paiement', 'date_paiement')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'montant', 'date_depense', 'hotel')
    list_filter = ('categorie', 'date_depense', 'hotel')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type_report', 'date_debut', 'date_fin', 'hotel')
    list_filter = ('hotel',)

from .models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('date', 'heure', 'client', 'chambre', 'statut', 'hotel')
    list_filter = ('statut', 'hotel')
