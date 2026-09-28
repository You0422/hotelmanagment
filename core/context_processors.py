from .models import HotelSetting


def user_role(request):
    """Rend le rôle et les droits d'accès disponibles dans tous les templates."""
    if request.user.is_authenticated:
        names = set(request.user.groups.values_list('name', flat=True))
        # Superuser : mêmes écrans / droits UI que le groupe Admin (souvent sans groupe assigné)
        is_admin = request.user.is_superuser or 'Admin' in names
        is_gerant = 'Gerant' in names
        return {
            'is_admin': is_admin,
            'is_gerant': is_gerant,
            'can_manage_expenses': is_admin or is_gerant,
        }
    return {'is_admin': False, 'is_gerant': False, 'can_manage_expenses': False}


def hotel_context(request):
    """
    Injecte `hotel_settings` dans tous les templates.
    - Utilisateur connecté : l'hôtel de son profil
    - Non connecté (page login) : le premier hôtel existant (par défaut)
    """
    hotel = None

    if request.user.is_authenticated:
        try:
            hotel = request.user.profile.hotel
        except Exception:
            pass

    if hotel is None:
        hotel = HotelSetting.objects.first()

    return {'hotel_settings': hotel}
