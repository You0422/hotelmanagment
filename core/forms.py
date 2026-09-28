from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Room, Client, Reservation, Service, Payment, Expense, Report, HotelSetting, CalendarEvent


class HotelRegistrationForm(forms.Form):
    """Inscription d'un hôtel : informations de l'établissement + identifiants de connexion."""
    nom_etablissement = forms.CharField(max_length=255, label="Nom de l'établissement")
    adresse = forms.CharField(required=False, label="Adresse")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    email = forms.EmailField(required=False, label="Email")
    nom_gerant = forms.CharField(max_length=100, required=False, label="Nom du gérant")

    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmation du mot de passe")

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Les deux mots de passe ne correspondent pas.")
        elif p1:
            user = User(username=cleaned.get('username', ''), email=cleaned.get('email', ''))
            try:
                validate_password(p1, user)
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return cleaned

class RoomForm(forms.ModelForm):
    prix_nuit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        localize=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 25000',
            'min': '0',
            'step': '1',
        })
    )

    class Meta:
        model = Room
        fields = ['numero_chambre', 'type_chambre', 'prix_nuit', 'description', 'statut_actuel']
        widgets = {
            'numero_chambre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 101'
            }),
            'type_chambre': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Équipements (Ex: Clim, Wi-Fi, Balcon...)'
            }),
            'statut_actuel': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

class ReservationForm(forms.ModelForm):
    # On surcharge le champ client pour le rendre optionnel au niveau du formulaire
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False, # <--- C'est cette ligne qui change tout
        label="Sélectionner un client existant",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nouveau_client = forms.BooleanField(
        required=False,
        label="Client non enregistré (cocher pour ajouter un nouveau client)"
    )
    nouveau_nom = forms.CharField(required=False, label="Nom")
    nouveau_prenom = forms.CharField(required=False, label="Prénom")
    nouveau_type_document = forms.ChoiceField(
        required=False,
        choices=Client.TYPE_DOCUMENT,
        label="Type de document"
    
    )
    nouveau_numero_document = forms.CharField(required=False, label="Numéro du document")
    nouveau_telephone = forms.CharField(required=False, label="Téléphone")
    nouveau_email = forms.EmailField(required=False, label="Email")
    nouveau_adresse = forms.CharField(required=False, label="Adresse")

    class Meta:
        model = Reservation
        fields = ['client', 'chambre', 'date_arrivee', 'date_depart', 'statut_reser']
        widgets = {
            'date_arrivee': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    #  Validations
    def clean(self):
        cleaned = super().clean()
        if cleaned.get('nouveau_client'):
            # Exiger les champs minimaux pour créer un client
            required_fields = ['nouveau_nom', 'nouveau_prenom', 'nouveau_type_document', 'nouveau_numero_document']
            for f in required_fields:
                if not cleaned.get(f):
                    self.add_error(f, "Champ requis.")
        else:
            if not cleaned.get('client'):
                self.add_error('client', "Sélectionnez un client ou cochez 'Client non enregistré'.")
        return cleaned

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'nom',
            'prenom',
            'email',
            'telephone',
            'adresse',
            'type_document',
            'numero_document',
            'date_entree',
            'date_sortie',
        ]

        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du client'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du client'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse email'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse'
            }),
            'type_document': forms.Select(attrs={
                'class': 'form-control',
            }),
            'numero_document': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro du document'
            }),
            'date_entree': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'date_sortie': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }

    #  Validations
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and len(telephone) < 8:
            raise forms.ValidationError("Le numéro de téléphone est invalide.")
        return telephone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("L'adresse email est invalide.")
        return email


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['montant_paye', 'methode_paiement', 'reference_paiement']
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    #  Validations
    def clean_montant_paye(self):
        montant_paye = self.cleaned_data.get('montant_paye')
        if montant_paye < 0:
            raise forms.ValidationError("Le montant payé ne peut pas быть negatif.")
        return montant_paye

class ExpenseForm(forms.ModelForm):
    autre_categorie = forms.CharField(
        max_length=100, 
        required=False, 
        label="Précisez la catégorie", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_autre_categorie', 'placeholder': 'Ex: Achat fournitures'})
    )

    class Meta:
        model = Expense
        fields = ['categorie', 'autre_categorie', 'montant', 'date_depense', 'description', 'justificatif']
        widgets = {
            'date_depense': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'justificatif': forms.ClearableFileInput(attrs={
                'accept': 'image/*,.pdf',
                'class': 'form-control'
            }),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(Expense.CATEGORIES)
        cat = self.instance.categorie if self.instance and self.instance.pk else None
        
        # If editing an expense with a custom category not in the predefined list
        if cat and cat not in dict(choices):
            self.initial['categorie'] = 'Autres'
            self.initial['autre_categorie'] = cat
            
        self.fields['categorie'] = forms.ChoiceField(
            choices=choices, 
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_categorie'})
        )

    def clean(self):
        cleaned_data = super().clean()
        categorie = cleaned_data.get('categorie')
        autre_categorie = cleaned_data.get('autre_categorie')
        
        if categorie == 'Autres':
            if not autre_categorie:
                self.add_error('autre_categorie', 'Veuillez préciser la catégorie.')
            else:
                cleaned_data['categorie'] = autre_categorie
        return cleaned_data

    def clean_justificatif(self):
        fichier = self.cleaned_data.get('justificatif')
        if not fichier:
            return fichier
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf']
        ext = fichier.name.rsplit('.', 1)[-1].lower() if '.' in fichier.name else ''
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                f"Format non autorisé (.{ext}). Formats acceptés : image (JPG, PNG) ou PDF."
            )
        return fichier

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom_service', 'prix_service', 'description']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'

class HotelSettingForm(forms.ModelForm):
    class Meta:
        model = HotelSetting
        fields = '__all__'


class CalendarEventForm(forms.ModelForm):
    """Nouvel événement du calendrier ; clients et chambres limités à l'hôtel de l'utilisateur."""
    class Meta:
        model = CalendarEvent
        fields = ['client', 'chambre', 'date', 'heure', 'statut']

    def __init__(self, *args, hotel=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hotel:
            self.fields['client'].queryset = Client.objects.filter(hotel=hotel)
            self.fields['chambre'].queryset = Room.objects.filter(hotel=hotel)
