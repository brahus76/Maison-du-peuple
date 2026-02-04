"""
URL configuration for MDP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from maison import views
from MDP import settings

urlpatterns = [

    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('evenement/', views.evenements, name='evenements'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(template_name='maison/connexion.html'), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),
    path('reserver/', views.reserver, name='reservation'),
    path('mes-ticket/', views.liste_ticket, name='liste_ticket'),
    path('acheter-ticket/<int:evenement_id>/', views.acheter_ticket, name='acheter_ticket'),
    path('mes-reservations/', views.liste_reservations, name='liste_reservations'),
    path('annuler/<int:res_id>/', views.annuler_reservation, name='annuler_reservation'),
    path('staff/dashboard/', views.tableau_bord_staff, name='tableau_bord_staff'),
    path('staff/confirmer/<int:res_id>/', views.confirmer_reservation, name='confirmer_reservation'),
    path('staff/deconnexion/', views.deconnexion_staff, name='deconnexion_staff'),
    path('payer/<int:res_id>/', views.payer_reservation, name='payer_reservation'),
    path('facture/<int:res_id>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    path('staff/refuser/<int:res_id>/', views.refuser_reservation, name='refuser_reservation'),
    path('ticket/<int:ticket_id>/confirmation/',views.ticket_confirmation,name='ticket_confirmation'),
    path('staff/ticket/<int:ticket_id>/confirmer/',views.confirmer_ticket,name='confirmer_ticket'),
    path('tableau_bord_client',views.tableau_bord_client, name='tableau_bord_client'),
    path(
    'reservations/<int:res_id>/facture/',
    views.generer_facture_pdf,
    name='telecharger_facture'
),

path(
    'ticket/<int:ticket_id>/telecharger/',
    views.telecharger_ticket,
    name='telecharger_ticket'
),




    # path('achat_ticket/<int:event_id>/', views.commander_ticket, name='acheter_ticket'),

    path('ticket/<int:ticket_id>/telecharger/',views.telecharger_ticket, name='telecharger_ticket'),
    path('evenement/<int:evenement_id>/ticket/', views.acheter_ticket, name='acheter_ticket'),
    path('ticket/<int:ticket_id>/confirmation/', views.ticket_confirmation, name='ticket_confirmation'),

    # path('accounts/', include('django.contrib.auth.urls')),
    # path('evenement/<str:categorie>/',liste_evenements, name='page_categorie'),
    # path('reserver/', reserver_espace, name='reserver_espace'),
    # path('mes reservation/', ma_liste_reservations, name='liste_reservation'),
    # path('achat_ticket/<int:evenement_id>/', acheter_ticket, name='acheter_ticket'),
    # path('inscription/',creer_profil_client, name='creer_profil_client'),
    # path('connexion/', connexion_view, name='login'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
