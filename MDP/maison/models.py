
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django.core.mail import send_mail
from django.conf import settings
import uuid

# ---------------------------------------------------------
# 1. UTILISATEURS ET RÔLES (ADMIN, STAFF, CLIENT)
# ---------------------------------------------------------

from django.contrib.auth.models import AbstractUser, UserManager

class Client(AbstractUser):
    # Vos champs actuels
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True, db_column='user_name')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Ajoutez explicitement le manager ici :
    objects = UserManager()

    REQUIRED_FIELDS = ['email'] # Assurez-vous que 'telephone' n'y est pas s'il n'existe pas

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Espace(models.Model):
    nom = models.CharField(max_length=100)
    # Nouveau champ pour le nombre de places
    capacite = models.PositiveIntegerField(help_text="Nombre maximum de personnes")
    prix_journalier = models.DecimalField(max_digits=10, decimal_places=2)
    est_disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} ({self.capacite} places)"

class Acteur(models.Model):
    nom = models.CharField(max_length=25, db_column='nom')
    telephone = models.CharField(max_length=15, db_column='telephone')

    def __str__(self):
        return f"{self.nom}"

# ---------------------------------------------------------
# 3. ÉVÉNEMENTS ET HÉRITAGE
# ---------------------------------------------------------

class Evenement(models.Model):
    image = models.ImageField(upload_to='eventImage', blank=True, null=True)
    titre_stockage  = models.CharField(max_length=30, db_column='nom_titre')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    _nombre_de_places = models.SmallIntegerField(db_column='nombre_de_places')
    description = models.TextField(blank=True, null=True)
    espace = models.ManyToManyField('Espace')
    intervenant = models.ManyToManyField('Acteur')
    type_evenement = models.CharField(max_length=50, editable=False)

    class Meta:
        abstract = False

    @property
    def nom_titre(self):
        # Ici vous faites votre modification "au temps voulu"
        return f"{self.titre_stockage}"
    
    @nom_titre.setter
    def nom_titre(self, v):
        self.titre_stockage = v.capitalize()

    @property
    def est_urgent(self):
        # On transforme le datetime actuel en simple date (.date())
        maintenant = timezone.now()
        seuil = maintenant + timedelta(hours=24)
    
    # On vérifie si l'événement se termine entre maintenant et demain même heure
        return maintenant <= self.date_fin <= seuil

    @property
    def nombre_de_places(self): 
        return self._nombre_de_places
    
    @nombre_de_places.setter
    def nombre_de_places(self, v):
        if v < 0: 
            raise ValidationError("Le nombre de places ne peut être négatif.")
        self._nombre_de_places = v

    def __str__(self):
        return self.titre_stockage
# Classes filles (Héritage)


class EvenementEconomique(Evenement): 
    secteur = models.CharField(max_length=50)
    def save(self, *args, **kwargs):
        if not self.type_evenement:
            self.type_evenement = "Evènements Economique"
        super().save(*args, **kwargs)



class EvenementSocial(Evenement): 
    cause = models.CharField(max_length=50)
    def save(self, *args, **kwargs):
        if not self.type_evenement:
            self.type_evenement = "Evènements Social" # Initialisation automatique
        super().save(*args, **kwargs)




class EvenementCulturel(Evenement):
    genre = models.CharField(max_length=50)
    def save(self, *args, **kwargs):
        if not self.type_evenement:
            self.type_evenement = "Evènements Culturel" # Initialisation automatique
        super().save(*args, **kwargs)

class EvenementPolitique(Evenement):
    organisation = models.CharField(max_length=50)
    def save(self, *args, **kwargs):
        if not self.type_evenement:
            self.type_evenement = "Evènements Politique"
        super().save(*args, **kwargs)


class Reservation(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('paye', 'Payé'),
        ('annule', 'Annulé'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    espace = models.ForeignKey(Espace, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    facture_telechargee = models.BooleanField(default=False)


    def calculer_prix(self):
        # Calcule la durée en jours
        delta = self.date_fin - self.date_debut
        jours = delta.days if delta.days > 0 else 1 # Minimum 1 jour
        return jours * self.espace.prix_journalier

    def save(self, *args, **kwargs):
        # Calcule automatiquement le montant avant de sauvegarder en base
        if not self.montant_total:
            self.montant_total = self.calculer_prix()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Réservation de {self.client.nom} {self.client.prenom} pour {self.espace.nom}"

class CategoriePlace(models.TextChoices):
    STANDARD = 'STD', 'Standard'
    VIP = 'VIP', 'VIP'
    VVIP = 'VVIP', 'VVIP'

class TarifEvenement(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='tarifs')
    categorie = models.CharField(max_length=10, choices=CategoriePlace.choices)
    prix = models.PositiveIntegerField()

    class Meta:
        unique_together = ('evenement', 'categorie') # Contrainte d'unicité
        verbose_name = "Tarif de l'événement"
        verbose_name_plural = "Tarifs des événements"
        ordering = ['prix'] # Les tarifs seront triés par prix croissant par défaut

    def __str__(self):
        return f"{self.evenement.nom_titre} - {self.get_categorie_display()} ({self.prix} FCFA)"


class Ticket(models.Model):

    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('annule', 'Annulé'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    choix_tarif = models.ForeignKey(TarifEvenement, on_delete=models.PROTECT)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )

    est_paye = models.BooleanField(default=False)
    code_barre_qr = models.CharField(max_length=150, blank=True)
    numero_place = models.IntegerField()
    date_achat = models.DateTimeField(auto_now_add=True)
    ticket_telecharge = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        # 🎟️ Nouveau ticket
        if not self.pk:
            evenement = self.choix_tarif.evenement

            if evenement.nombre_de_places <= 0:
                raise ValidationError("Plus de places disponibles.")

            # Numéro de place
            dernier_ticket = Ticket.objects.filter(
                choix_tarif__evenement=evenement
            ).count()
            self.numero_place = dernier_ticket + 1

            # Décrémenter les places
            evenement.nombre_de_places -= 1
            evenement.save()

        # 🔐 Générer le code QR s'il n'existe pas
        if not self.code_barre_qr:
            self.code_barre_qr = f"TICKET-{uuid.uuid4()}"

        # 💳 Statut paiement
        self.est_paye = (self.statut == 'paye')

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def montant(self):
        return self.choix_tarif.prix

    @property
    def evenement(self):
        return self.choix_tarif.evenement

    def __str__(self):
        return f"Ticket {self.code_barre_qr}"

class Facture(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='factures_recues')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True}, related_name='factures_creees')
    espace = models.ForeignKey('Espace', on_delete=models.PROTECT) # Indispensable pour le calcul
    
    date_emission = models.DateField(default=timezone.now)
    nombre_jour = models.PositiveIntegerField(default=1)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    
    statut = models.CharField(max_length=20, choices=[('PAYEE', 'Payée'), ('ATTENTE', 'En attente')], default='ATTENTE')

    def save(self, *args, **kwargs):
        # Le calcul utilise maintenant le champ 'espace' bien défini
        if self.espace:
            self.montant_total = self.espace.prix_journalier * self.nombre_jour
        super().save(*args, **kwargs)

    def envoyer_par_email(self):
        # Logique simplifiée pour l'envoi
        sujet = f"Votre facture N° {self.id}"
        message = f"Bonjour {self.client.nom}, le montant de votre facture est de {self.montant_total}€."
        send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [self.client.email])

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']

    def __str__(self):
        return f"Facture N° {self.id} - {self.client.nom}"
