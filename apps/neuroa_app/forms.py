import datetime
from dataclasses import fields

from django import forms
from django.core.exceptions import ValidationError
from .models import User, Candidate, Experience, Attribute, ExperienceContractTypeEnum, RQTHEnum, CandidateRemoteEnum, \
    CandidateMobilityEnum, ExperienceTypeEnum, WorkTimeEnum

BOOL_CHOICES = [(True, 'Oui'), (False, 'Non')]

# Définir les choix pour les mois
MONTH_CHOICES = [
    (1, 'Janvier'),
    (2, 'Février'),
    (3, 'Mars'),
    (4, 'Avril'),
    (5, 'Mai'),
    (6, 'Juin'),
    (7, 'Juillet'),
    (8, 'Août'),
    (9, 'Septembre'),
    (10, 'Octobre'),
    (11, 'Novembre'),
    (12, 'Décembre'),
]

EXPERIENCE_TYPE_INFOS = {
    'pro': {
        'type_label': "Expérience professionnelle",
        'name_label': "Poste :",
        'organization_label': "Organisation :",
        'is_current_label': "J'occupe actuellement ce poste :",
    },
    'training': {
        'type_label': "Formation",
        'name_label': "Diplôme :",
        'organization_label': "École :",
        'is_current_label': "Je suis actuellement en formation :",
    },
    'personal': {
        'type_label': "Activité personnelle",
        'name_label': "Titre :",
        'organization_label': "Organisation :",
        'is_current_label': "Je pratique actuellement cette activité :",
    }
}

# Définir les choix pour les années (100 ans avant l'année actuelle pour la date de début)
current_year = datetime.datetime.now().year
YEAR_CHOICES_START = [(year, year) for year in range(current_year - 100, current_year + 1)]

# Définir les choix pour les années (plus ou moins 100 ans pour la date de fin)
YEAR_CHOICES_END = [(year, year) for year in range(current_year - 100, current_year + 101)]

class StylesFormMixin:
    def add_styles_and_placeholders(self, styles):
        for name, field in self.fields.items():
            if name not in ["mobilities", "start_month", "start_year", "end_month", "end_year"]:
                old_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{old_classes} {styles}".strip()

            if name in ["start_month", "start_year", "end_month", "end_year"]:
                old_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{old_classes} 'h-10 pl-3 text-sm font-roboto mt-0.5 mr-3.5 border-[var(--border_color_primary)] rounded outline-none'".strip()

            if isinstance(field, (forms.CharField, forms.URLField)):
                label = field.label if field.label else name.replace('_', ' ')
                field.widget.attrs['placeholder'] = f"Saisissez votre {label.lower()} ...".capitalize()

# FORMULAIRE POUR SIGN UP FORM
class SignUpForm(StylesFormMixin, forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.CharField(max_length=20)
    conditions_accepted = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = ""
        self.add_styles_and_placeholders(base_classes)

    def save(self):
        user = User.objects.create_user(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
            conditions_accepted=self.cleaned_data['conditions_accepted']
        )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'description', 'photo']

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['city', 'country', 'job', 'rqth', 'candidate_remote', 'special_needs_comments', 'mobilities']

# FORMULAIRE POUR BASIC INFOS (CANDIDAT)
class BasicInfoForm(StylesFormMixin, forms.Form):
    first_name = forms.CharField(label="Prénom :", required=True)
    last_name = forms.CharField(label="Nom :", required=True)
    job = forms.CharField(label="Poste recherché :", required=False)
    description = forms.CharField(label="Présentation :", required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        base_classes = "w-[280px] h-10 pl-3 text-sm font-roboto mt-0.5 border-[var(--border_color_primary)] rounded md:w-[590px] outline-none"
        self.add_styles_and_placeholders(base_classes)

    def save(self):
        if self.user and self.candidate:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.description = self.cleaned_data['description']
            self.user.save()
            self.candidate.job = self.cleaned_data['job']
            self.candidate.save()

# FORMULAIRE POUR INFORMATIONS CANDIDAT (VOS INFOS)
class CandidateInfoForm(StylesFormMixin, forms.Form):
    city = forms.CharField(label="Ville :", max_length=50, required=True)
    country = forms.CharField(label="Pays :", max_length=50, required=True)
    mobilities = forms.MultipleChoiceField(label="Mobilité :", choices=CandidateMobilityEnum.choices, required=False)
    candidate_remote = forms.ChoiceField(
        label="Télétravail souhaité :",
        choices=[('', 'Sélectionnez')] + list(CandidateRemoteEnum.choices),
        required=False
    )
    rqth = forms.ChoiceField(
        label="RQTH :",
        choices=[('', 'Sélectionnez')] + list(RQTHEnum.choices),
        required=False
    )
    special_needs_comments = forms.CharField(label="Besoins d'adaptation des conditions de travail :", widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        base_classes = "w-[280px] h-10 pl-3 text-sm font-roboto mt-0.5 border-[var(--border_color_primary)] rounded md:w-[590px] outline-none"
        self.add_styles_and_placeholders(base_classes)

    def save(self):
        if self.candidate:
            self.candidate.city = self.cleaned_data['city']
            self.candidate.country = self.cleaned_data['country']
            self.candidate.rqth = self.cleaned_data['rqth']
            self.candidate.candidate_remote = self.cleaned_data['candidate_remote']
            self.candidate.mobilities = self.cleaned_data['mobilities']
            self.candidate.special_needs_comments = self.cleaned_data['special_needs_comments']
            self.candidate.save()

# FORMULAIRE POUR EXPERIENCES PRO + ACTIVITES PRO + ACTIVITE PERSO + FORMATIONS
class ExperienceForm(StylesFormMixin, forms.ModelForm):
    name = forms.CharField(label="Titre :", required=True)
    city = forms.CharField(label="Ville :", required=False)
    country = forms.CharField(label="Pays :", required=False)
    experience_contract_type = forms.ChoiceField(
        label="Type d'emploi :",
        choices=[('', 'Sélectionnez')] + list(ExperienceContractTypeEnum.choices),
        required=True
    )
    experience_work_time = forms.ChoiceField(
        label="Temps de travail :",
        choices=[('', 'Sélectionnez')] + list(WorkTimeEnum.choices),
        required=True
    )
    start_month = forms.ChoiceField(
        label="Mois :",
        choices=[('', 'Mois')] + MONTH_CHOICES,
        required=True
    )
    start_year = forms.ChoiceField(
        label="Année :",
        choices=[('', 'Année')] + YEAR_CHOICES_START,
        required=True
    )
    end_month = forms.ChoiceField(
        label="Mois :",
        choices=[('', 'Mois')] + MONTH_CHOICES,
        required=False
    )
    end_year = forms.ChoiceField(
        label="Année :",
        choices=[('', 'Année')] +YEAR_CHOICES_END,
        required=False
    )
    is_current_position = forms.ChoiceField(
        label="Je pratique actuellement cette activité :",
        choices=[('', 'Sélectionnez')] + BOOL_CHOICES,
        required=True
    )
    url = forms.URLField(label="Lien :", required=False)
    description = forms.CharField(
        label="Détails :",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    class Meta:
        model = Experience
        fields = ['name', 'organization', 'city', 'country', 'experience_contract_type', 'experience_work_time',
                  'start_month', 'start_year', 'end_month', 'end_year', 'is_current_position', 'url', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = "w-72 h-10 pl-3 text-sm font-roboto mt-0.5 border-[var(--border_color_primary)] rounded md:w-[275px] outline-none"
        self.add_styles_and_placeholders(base_classes)

        experience_type = None
        if 'initial' in kwargs and 'experience_type' in kwargs['initial']:
            experience_type = kwargs['initial']['experience_type']
        elif len(args) > 0 and 'experience_type' in args[0]:
            experience_type = args[0].get('experience_type')

        if experience_type != 'pro':
            self.fields['experience_contract_type'].required = False
            self.fields['experience_work_time'].required = False
        else:
            self.fields['experience_contract_type'].required = True
            self.fields['experience_work_time'].required = True

    def clean(self):
        cleaned_data = super().clean()
        start_month = cleaned_data.get('start_month')
        start_year = cleaned_data.get('start_year')
        end_month = cleaned_data.get('end_month')
        end_year = cleaned_data.get('end_year')
        is_current_position = cleaned_data.get('is_current_position')
        experience_type = self.data.get('experience_type')

        # Convertir is_current_position en booléen
        if isinstance(is_current_position, str):
            is_current_position = is_current_position.lower() in ['true', '1', 'yes', 'oui']
            cleaned_data['is_current_position'] = is_current_position

        if experience_type == 'pro':
            if not cleaned_data.get('experience_contract_type'):
                self.add_error('experience_contract_type',
                               "Ce champ est obligatoire pour une expérience professionnelle.")
            if not cleaned_data.get('experience_work_time'):
                self.add_error('experience_work_time', "Ce champ est obligatoire pour une expérience professionnelle.")

        if not start_month or not start_year:
            raise forms.ValidationError("Le mois et l'année de début sont obligatoires.")

        if not end_month or not end_year :

            if is_current_position:
                cleaned_data['end_month'] = None
                cleaned_data['end_year'] = None
            else:
                raise forms.ValidationError(
                    "Le mois et l'année de fin sont obligatoires si ce n'est pas votre poste actuel.")

        if start_month and (int(start_month) < 1 or int(start_month) > 12):
            self.add_error('start_month', "Le mois de début doit être compris entre 1 et 12.")

        if end_month and (int(end_month) < 1 or int(end_month) > 12):
            self.add_error('end_month', "Le mois de fin doit être compris entre 1 et 12.")

        if start_year and (int(start_year) < current_year - 100 or int(start_year) > current_year + 100):
            self.add_error('start_year',
                           f"L'année de début doit être comprise entre {current_year - 100} et {current_year + 100}.")

        if end_year and (int(end_year) < current_year - 100 or int(end_year) > current_year + 100):
            self.add_error('end_year',
                           f"L'année de fin doit être comprise entre {current_year - 100} et {current_year + 100}.")

        if (start_month and (1 < int(start_month) < 12)) and (
                start_year and (current_year - 100 < int(start_year) < current_year + 100)) and (
                end_month and (1 < int(end_month) < 12)) and (
                end_year and (current_year - 100 < int(end_year) < current_year + 100)):

            start_date = datetime.date(int(start_year), int(start_month), 1)
            end_date = datetime.date(int(end_year), int(end_month), 1)
            if end_date < start_date:
                raise forms.ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

        return cleaned_data

# FORMULAIRE COMPETENCES + LOISIR, PASSIONS + CAUSES, ENGAGEMENTS
class AttributeForm(StylesFormMixin, forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name']

    name = forms.CharField(
        widget=forms.Textarea(attrs={
            'maxlength': '300',
            'rows': 3,
            'placeholder': ''  # Initialisé vide
        }),
        help_text="Séparez les éléments par des virgules (max 50 caractères par élément)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = "w-[280px] h-10 pl-3 text-sm font-roboto mt-0.5 border-[var(--border_color_primary)] rounded md:w-[520px] outline-none"
        self.add_styles_and_placeholders(base_classes)

    def clean_name(self):
        value = self.cleaned_data['name']
        if len(value) > 300:
            raise ValidationError("La saisie totale dépasse 300 caractères")

        entries = [n.strip() for n in value.split(',') if n.strip()]
        for entry in entries:
            if len(entry) > 50:
                raise ValidationError(f"'{entry}' dépasse 50 caractères")

        if not entries:
            raise forms.ValidationError("Veuillez saisir au moins un élément")
        return entries

