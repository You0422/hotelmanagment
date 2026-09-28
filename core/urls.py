from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscription/', views.register_view, name='register'),

    # Accueil
    path('', views.home, name='home'),

    # Chambres
    path('chambres/', views.rooms_list, name='rooms_list'),
    path('chambres/ajouter/', views.room_create, name='room_create'),
    path('chambres/<int:pk>/', views.room_detail, name='room_detail'),
    path('chambres/modifier/<int:pk>/', views.room_update, name='room_update'),
    path('chambres/supprimer/<int:pk>/', views.room_delete, name='room_delete'),

    # Clients
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/ajouter/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/modifier/<int:pk>/', views.client_update, name='client_update'),
    path('clients/supprimer/<int:pk>/', views.client_delete, name='client_delete'),
    path('clients/<int:pk>/pdf/', views.client_pdf, name='client_pdf'),

    # Réservations
    path('reservations/', views.reservations_list, name='reservations_list'),
    path('reservations/ajouter/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/modifier/<int:pk>/', views.reservation_update, name='reservation_update'),
    path('reservations/supprimer/<int:pk>/', views.reservation_delete, name='reservation_delete'),
    
    # Calendrier
    path('calendrier/', views.calendar_view, name='calendar'),
    path('calendrier/evenements/ajouter/', views.calendar_event_create, name='calendar_event_create'),
    path('calendrier/evenements/<int:pk>/statut/', views.calendar_event_status, name='calendar_event_status'),
    path('calendrier/evenements/<int:pk>/supprimer/', views.calendar_event_delete, name='calendar_event_delete'),

    # Actions de séjour
    path('reservations/<int:pk>/checkin/', views.reservation_checkin, name='reservation_checkin'),
    path('reservations/<int:pk>/checkout/', views.reservation_checkout, name='reservation_checkout'),
    path('reservations/<int:pk>/annuler/', views.reservation_cancel, name='reservation_cancel'),
    path('reservations/<int:pk>/facture/', views.reservation_invoice, name='reservation_invoice'),
    
    # Paiements et Services liés
    path('reservations/<int:pk>/ajouter-service/', views.reservation_add_service, name='reservation_add_service'),
    path('reservations/<int:pk>/services/<int:service_pk>/supprimer/', views.reservation_delete_service, name='reservation_delete_service'),
    path('reservations/<int:pk>/ajouter-paiement/', views.reservation_add_payment, name='reservation_add_payment'),

    # Services (Catalogue)
    path('services/', views.services_list, name='services_list'),
    path('services/ajouter/', views.service_create, name='service_create'),
    path('services/modifier/<int:pk>/', views.service_update, name='service_update'),
    path('services/supprimer/<int:pk>/', views.service_delete, name='service_delete'),
    
    #PAIEMENTS   
    path('paiements/', views.payment_list, name='payment_list'),
    path('paiements/ajouter/', views.payment_create, name='payment_create'),
    path('paiements/<int:pk>/recu/', views.payment_receipt, name='payment_receipt'),

    # Dépenses
    path('depenses/', views.expenses_list, name='expenses_list'),
    path('depenses/ajouter/', views.expenses_create, name='expenses_create'),
    path('depenses/modifier/<int:pk>/', views.expenses_update, name='expenses_update'),
    path('depenses/supprimer/<int:pk>/', views.expenses_delete, name='expenses_delete'),

    # Rapports et Paramètres
    path('rapports/', views.reports, name='reports'),
    path('rapports/upload/', views.report_upload, name='report_upload'),
    path('rapports/export/pdf/', views.report_export_pdf, name='report_export_pdf'),
    path('rapports/export/excel/', views.report_export_excel, name='report_export_excel'),
    path('parametres/', views.settings_view, name='settings_view'),
    path('parametres/donnees-exemple/', views.settings_sample_data, name='settings_sample_data'),
]
