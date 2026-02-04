from django import forms 
from .models import Reservation, Client, Ticket, TarifEvenement
from django.contrib.auth.forms import UserCreationForm



class TicketAchatForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # On n'affiche que le choix du tarif au client
        # Le client, le QR code et le numéro de place seront gérés en arrière-plan
        fields = ['choix_tarif']
        widgets = {
            'choix_tarif': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    def __init__(self, *args, **kwargs):
        # On récupère l'événement passé depuis la vue pour filtrer les tarifs
        self.evenement = kwargs.pop('evenement', None)
        super().__init__(*args, **kwargs)
        
        if self.evenement:
            # On affiche uniquement les tarifs liés à cet événement précis
            self.fields['choix_tarif'].queryset = TarifEvenement.objects.filter(evenement=self.evenement)
            self.fields['choix_tarif'].label = "Choisir votre catégorie de place"

    def clean(self):
        """Vérification globale du stock avant validation"""
        cleaned_data = super().clean()
        if self.evenement and self.evenement.nombre_de_places <= 0:
            raise forms.ValidationError("Désolé, cet événement est complet.")
        return cleaned_data

class ClientRegistrationForm(UserCreationForm):
    # On définit les champs supplémentaires avec les classes Bootstrap
    prenom = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    nom = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@mail.com'})
    )
    phone = forms.CharField(
        label="Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0123456789'})
    )

    class Meta(UserCreationForm.Meta):
        model = Client
        # UserCreationForm.Meta.fields contient déjà 'username'
        # On y ajoute nos champs personnalisés
        fields = UserCreationForm.Meta.fields + ("prenom", "nom", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout automatique de la classe form-control aux champs de mot de passe par défaut
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['espace', 'date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'espace': forms.Select(attrs={'class': 'form-control'}),
        }