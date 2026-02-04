from .forms import ClientRegistrationForm, ReservationForm
from django.contrib.auth import login, logout, authenticate
from django.core.mail import EmailMessage
from django.utils import timezone 
from maison import models
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Evenement, Ticket
from .forms import TicketAchatForm
from django.db.models import Sum





import qrcode
import io
import base64
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse


import qrcode
import io
import base64


from .forms import TicketAchatForm


def generer_qr_reservation_base64(reservation):
    # Données à encoder dans le QR Code
    data = f"Facture MDP-{reservation.id}\nClient: {reservation.client.username}\nMontant: {reservation.montant_total} FCFA"
    
    # Création de l'objet QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    # Création de l'image
    img = qr.make_image(fill_color="black", back_color="white")

    # Conversion de l'image en base64 pour l'intégration HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()





def generer_qr_ticket_base64(ticket):
    # Données à encoder dans le QR Code
    data = f"Ticket MDP-{ticket.id}\nClient: {ticket.client.username}\nMontant: {ticket.choix_tarif.prix} FCFA"
    
    # Création de l'objet QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    # Création de l'image
    img = qr.make_image(fill_color="black", back_color="white")

    # Conversion de l'image en base64 pour l'intégration HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# @login_required
# def generer_facture_pdf(request, res_id):

#     if request.user.is_staff:
#         reservation = get_object_or_404(models.Reservation, id=res_id)
#     else:
#         reservation = get_object_or_404(models.Reservation, id=res_id, client=request.user)
    
#     # Sécurité : Seules les réservations payées ont une facture
#     if reservation.statut != 'paye':
#         return redirect('liste_reservations')

#     if not reservation.facture_telechargee:
#         reservation.facture_telechargee = True
#         reservation.save(update_fields=['facture_telechargee'])

#     # Génération du QR Code
#     qr_data = f"Facture MDP-{reservation.id}\nClient: {reservation.client.username}\nMontant: {reservation.montant_total} FCFA"
#     qr = qrcode.make(qr_data)
    
#     # Convertir le QR code en format lisible par le HTML (Base64)
#     buffer = io.BytesIO()
#     qr.save(buffer, format="PNG")
#     qr_base64 = base64.b64encode(buffer.getvalue()).decode()

#     context = {
#         'reservation': reservation,
#         'qr_code': qr_base64,
#     }
    
    # Rendu PDF
    template = get_template('reservations/facture_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_{res_id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    return response



@login_required
def generer_facture_pdf(request, res_id):

    if request.user.is_staff:
        reservation = get_object_or_404(models.Reservation, id=res_id)
    else:
        reservation = get_object_or_404(
            models.Reservation,
            id=res_id,
            client=request.user
        )

    # Sécurité
    if reservation.statut != 'paye':
        return redirect('liste_reservations')

    # ✅ MARQUER COMME TÉLÉCHARGÉ
    if not reservation.facture_telechargee:
        reservation.facture_telechargee = True
        reservation.save(update_fields=['facture_telechargee'])

    # Génération QR
    qr_data = f"Facture MDP-{reservation.id}"
    qr = qrcode.make(qr_data)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'reservation': reservation,
        'qr_code': qr_base64,
    }

    template = get_template('reservations/facture_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="Facture_{reservation.id}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response







@login_required
def generer_ticket_pdf(request, tick_id):

    if request.user.is_staff:
        ticket = get_object_or_404(models.Ticket, id=tick_id)
    else:
        ticket = get_object_or_404(models.Ticket, id=tick_id, client=request.user)
    
    # Sécurité : Seules les réservations payées ont une facture
    if ticket.statut != 'paye':
        return redirect('liste_ticket')

    # Génération du QR Code
    qr_data = f"Facture MDP-{ticket.id}\nClient: {ticket.client.username}\nMontant: {ticket.choix_tarif.prix} FCFA"
    qr = qrcode.make(qr_data)
    
    # Convertir le QR code en format lisible par le HTML (Base64)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'ticket': ticket,
        'qr_code': qr_base64,
    }
    
    # Rendu PDF
    template = get_template('tickets/ticket_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_{tick_id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    return response




@login_required
def payer_reservation(request, res_id):
    reservation = get_object_or_404(
        models.Reservation,
        id=res_id,
        client=request.user
    )

    if reservation.statut == 'paye':
        messages.info(request, "Cette réservation est déjà payée.")
        return redirect('liste_reservations')

    try:
        # ✅ PAIEMENT (CRITIQUE)
        reservation.statut = 'paye'
        reservation.save()

    except Exception as e:
        print("ERREUR PAIEMENT :", e)
        messages.error(request, "Le paiement a échoué.")
        return redirect('liste_reservations')

    # 🔹 ACTIONS NON CRITIQUES
    try:
        qr_code = generer_qr_reservation_base64(reservation)
        envoyer_facture_email(reservation, qr_code)
    except Exception as e:
        print("ERREUR EMAIL / QR :", e)
        messages.warning(
            request,
            "Paiement réussi, mais l'envoi de la facture a échoué."
        )
        return redirect('liste_reservations')

    messages.success(request, "Paiement effectué avec succès.")
    return redirect('liste_reservations')





@login_required
def payer_ticket(request, tick_id):
    ticket = get_object_or_404(
        Ticket,
        id=tick_id,
        client=request.user
    )

    if ticket.statut != 'en_attente':
        messages.error(request, "Ce ticket ne peut pas être payé.")
        return redirect('liste_ticket')

    try:
        ticket.statut = 'paye'
        ticket.save()

        qr_code = generer_qr_ticket_base64(ticket)
        envoyer_facture_email(ticket, qr_code)

        messages.success(request, "Paiement du ticket validé.")

    except Exception as e:
        print(e)
        messages.error(request, "Erreur lors du paiement.")

    return redirect('liste_ticket')






def index(request):
    # On récupère le dernier ajouté (.last()) ou le premier (.first())
    context = {
        'culturel': models.EvenementCulturel.objects.last(),
        'politique': models.EvenementPolitique.objects.last(),
        'economique': models.EvenementEconomique.objects.last(),
        'social': models.EvenementSocial.objects.last(),
    }
    return render(request, 'maison/index.html', context)


from django.utils import timezone

def evenements(request):
    today = timezone.now().date()

    # Événements à venir + en cours
    evenements = Evenement.objects.filter(
        date_fin__gte=today
    ).order_by('date_debut')

    acteurs = models.Acteur.objects.all()

    context = {
        'Evenement': evenements,
        'acteurs': acteurs
    }
    return render(request, 'maison/evenement.html', context)





def est_en_cours(self):
    today = timezone.now().date()
    return self.date_debut <= today <= self.date_fin



def inscription(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            # .save() ici appellera la logique de UserCreationForm 
            # qui utilise correctement create_user
            form.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"Compte créé avec succès pour {username} !")
            return redirect('connexion')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'maison/inscription.html', {'form': form})

def connexion(request):
    next_page = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == 'POST':
        username = request.POST['username']
        password= request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect(next_page)
        else: 
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    return render(request, 'maison/connexion.html',{'next': next_page})

def deconnexion(request):
    logout(request)
    return redirect('index')

@login_required
def deconnexion_staff(request):
    logout(request)
    return redirect('staff/dashboard')

@login_required
def reserver(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # 1. On prépare l'objet à enregistrer (PAS ENCORE DE QUERYSET ICI)
            nouvelle_res = form.save(commit=False)
            nouvelle_res.client = request.user 
            nouvelle_res.statut = 'en_attente' # Par défaut

            # 2. Vérification de la disponibilité
            # On cherche s'il existe DEJA des réservations qui occupent ce créneau
            chevauchement = models.Reservation.objects.filter(
                espace=nouvelle_res.espace,
                date_debut__lt=nouvelle_res.date_fin,
                date_fin__gt=nouvelle_res.date_debut
            ).exclude(statut='annule').exists()

            if chevauchement:
                messages.error(request, "Cet espace est déjà réservé pour ces dates.")
            elif nouvelle_res.date_debut >= nouvelle_res.date_fin:
                messages.error(request, "La date de début doit être antérieure à la date de fin.")
            else:
                # 3. Sauvegarde de l'objet unique
                nouvelle_res.save() 
                messages.success(request, "Demande envoyée ! En attente de confirmation du staff.")
                return redirect('liste_reservations') 
    else:
        form = ReservationForm()
    
    # On renvoie uniquement le formulaire pour la page de réservation
    return render(request, 'reservations/reserver.html', {'form': form})

@login_required
def liste_reservations(request):
    # On récupère uniquement les réservations du client connecté
    mes_reservations = models.Reservation.objects.filter(client=request.user).order_by('-date_debut')
    return render(request, 'reservations/liste_reservations.html', {
        'reservations': mes_reservations
    })

def liste_ticket(request):
    mes_tickets = models.Ticket.objects.filter(client=request.user).order_by('-date_achat')
    return render(request, 'tickets/liste_ticket.html', {'tickets': mes_tickets})


# maison/views.py


@login_required
def valider_reservation(request, res_id):
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('liste_reservations')
        
    reservation = get_object_or_404(models.Reservation, id=res_id)
    reservation.statut = 'confirme'
    reservation.save()
    messages.success(request, f"La réservation de {reservation.client} est confirmée.")
    return redirect('liste_reservations')


@login_required
def valider_ticket(request, tick_id):
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('liste_ticket')
        
    ticket = get_object_or_404(models.Ticket, id=tick_id)
    ticket.statut = 'paye'
    ticket.save()
    messages.success(request, f"La réservation de {ticket.client} est confirmée.")
    return redirect('liste_ticket')


@login_required
def annuler_reservation(request, res_id):
    # On récupère la réservation uniquement si elle appartient au client
    reservation = get_object_or_404(models.Reservation, id=res_id, client=request.user)
    
    if reservation.statut == 'attente':
        reservation.statut = 'annule'
        reservation.save()
        messages.success(request, "Votre réservation a été annulée.")
    else:
        messages.error(request, "Impossible d'annuler une réservation déjà confirmée ou payée.")
        
    return redirect('liste_reservations')




@login_required
def annuler_ticket(request, tick_id):
    # On récupère la réservation uniquement si elle appartient au client
    ticket = get_object_or_404(models.Reservation, id=tick_id, client=request.user)
    
    if ticket.statut == 'attente':
        ticket.statut = 'annule'
        ticket.save()
        messages.success(request, "Votre achat de ticket a été annulée.")
    else:
        messages.error(request, "Impossible d'annuler l'achat déjà confirmée ou payée.")
        
    return redirect('liste_ticket')





@login_required
def refuser_reservation(request, res_id):
    if not request.user.is_staff:
        messages.error(request, "Accès interdit.")
        return redirect('index')

    reservation = get_object_or_404(models.Reservation, id=res_id)
    
    # On passe le statut à annulé
    reservation.statut = 'annule'
    reservation.save()
    
    messages.warning(request, f"La réservation #{res_id} a été refusée.")
    return redirect('tableau_bord_staff')


    # On récupère les réservations qui attendent une action
    reservations_en_attente = Reservation.objects.filter(statut='en_attente').order_by('date_debut')
    
    context = {
        'reservations_en_attente': reservations_en_attente,
    }
    return render(request, 'maison/tableau_bord_staff.html', context)

@staff_member_required
def confirmer_reservation(request, res_id):
    reservation = get_object_or_404(models.Reservation, id=res_id)
    reservation.statut = 'confirme' # Change le statut de 'attente' à 'confirme'
    reservation.save()
    messages.success(request, f"Réservation #{res_id} confirmée !")
    return redirect('tableau_bord_staff')


def envoyer_facture_email(reservation, qr_code_base64):
    subject = f"Votre facture pour la réservation #{reservation.id} - Maison Du Peuple"
    
    # Corps du mail en HTML
    message_html = render_to_string('emails/confirmation_paiement.html', {
        'user': reservation.client,
        'reservation': reservation
    })

    # Génération du PDF en mémoire (sans l'enregistrer sur le disque)
    template = get_template('reservations/facture_pdf.html')
    html_content = template.render({'reservation': reservation, 'qr_code': qr_code_base64})
    
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)
    pdf_value = pdf_file.getvalue()

    # Création de l'e-mail
    email = EmailMessage(
        subject,
        message_html,
        'votre-email@gmail.com',
        [reservation.client.email],
    )
    email.content_subtype = "html"  # Pour envoyer le corps en HTML
    
    # Attacher le PDF
    email.attach(f'Facture_MDP_{reservation.id}.pdf', pdf_value, 'application/pdf')
    
    email.send()




@login_required
def acheter_ticket(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    if evenement.nombre_de_places <= 0:
        messages.error(request, "Cet événement est complet.")
        return redirect('liste_evenements')
    if request.method == 'POST':
        form = TicketAchatForm(request.POST, evenement=evenement)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.client = request.user  # Client connecté
            ticket.save()
            messages.success(request,f"Ticket acheté avec succès - "f"{ticket.choix_tarif.get_categorie_display()} "f"({ticket.montant} FCFA)")
            return redirect('ticket_confirmation', ticket_id=ticket.id)
    else:
        form = TicketAchatForm(evenement=evenement)

    context = {
        'evenement': evenement,
        'form': form
    }

    return render(request, 'tickets/acheter_ticket.html', context)


@login_required
def ticket_confirmation(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, client=request.user)

    return render(request, 'tickets/confirmation.html', {
        'ticket': ticket
    })

@staff_member_required
def confirmer_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    ticket.statut = 'paye'
    ticket.save()

    messages.success(
        request,
        f"Ticket #{ticket.id} confirmé. Le client peut maintenant le télécharger."
    )
    return redirect('tableau_bord_staff')



@login_required
def telecharger_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        client=request.user,
        est_paye=True 
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    p = canvas.Canvas(response)

    # 🧾 CONTENU DU TICKET
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "🎟️ TICKET D'ÉVÉNEMENT")
    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Événement : {ticket.evenement.nom_titre}")
    p.drawString(50, 740, f"Catégorie : {ticket.choix_tarif.get_categorie_display()}")
    p.drawString(50, 720, f"Prix : {ticket.montant} FCFA")
    p.drawString(50, 700, f"Numéro de place : {ticket.numero_place}")
    p.drawString(50, 680, f"Client : {ticket.client.prenom} {ticket.client.nom}")
    p.drawString(50, 660, f"Date d'achat : {ticket.date_achat.strftime('%d/%m/%Y')}")
    p.showPage()
    p.save()


    if not ticket.ticket_telecharge:
        ticket.ticket_telecharge = True
        ticket.save(update_fields=['ticket_telecharge'])

    return response


@staff_member_required
def tableau_bord_staff(request):

    reservations_en_attente = models.Reservation.objects.filter(
        statut='en_attente'
    ).order_by('date_debut')

    tickets_en_attente = Ticket.objects.filter(
        statut='en_attente'
    ).order_by('-date_achat')

    context = {
        'reservations_en_attente': reservations_en_attente,
        'tickets_en_attente': tickets_en_attente,
    }

    return render(request, 'maison/tableau_bord_staff.html', context)



@login_required
def tableau_bord_client(request):
    user = request.user
    now = timezone.now()

    mois = now.month
    annee = now.year  # utilisé en interne seulement

    total_evenements = Evenement.objects.filter(
        date_debut__month=mois,
        date_debut__year=annee
    ).count()

    total_tickets = Ticket.objects.filter(
        client=user,
        statut='paye',
        date_achat__month=mois,
        date_achat__year=annee
    ).count()

    total_reservations = models.Reservation.objects.filter(
        client=user,
        date_debut__month=mois,
        date_debut__year=annee
    ).filter(
        Q(statut='confirme') | Q(statut='paye')
    ).count()

    total_depense_tickets = Ticket.objects.filter(
        client=user,
        statut='paye',
        date_achat__month=mois,
        date_achat__year=annee
    ).aggregate(total=Sum('choix_tarif__prix'))['total'] or 0

    total_depense_reservations = models.Reservation.objects.filter(
        client=user,
        statut='paye',
        date_debut__month=mois,
        date_debut__year=annee
    ).aggregate(total=Sum('montant_total'))['total'] or 0

    total_depense = total_depense_tickets + total_depense_reservations


    context = {
        'mois': now.strftime('%B'),
        'total_evenements': total_evenements,
        'total_tickets': total_tickets,
        'total_reservations': total_reservations,
        'total_depense': total_depense,
    }

    return render(request, 'maison/tableau_bord_client.html', context)

