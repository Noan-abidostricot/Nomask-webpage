from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from django.utils import timezone
from multiselectfield import MultiSelectField
from django_prose_editor.fields import ProseEditorField
import uuid, re

class RoleEnum(models.TextChoices):
    CANDIDATE = 'candidate', _('Candidat')
    RECRUITER = 'recruiter', _('Recruteur')
    ADMIN = 'admin', _('Admin')

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, conditions_accepted=None, super_admin=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        if not role or role not in RoleEnum.values:
            raise ValueError('L\'utilisateur doit avoir un rôle valide')
        if not conditions_accepted:
            raise ValueError('L\'utilisateur doit approuver les conditions')

        # Valider le mot de passe
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, conditions_accepted=conditions_accepted, **extra_fields)
        user.set_password(password)
        user.is_email_valid = False

        # Utilisation d'une transaction pour garantir l'intégrité des données
        from django.db import transaction
        with transaction.atomic():
            user.save(using=self._db)

            # Création de l'entrée dans la table de rôle spécifique
            role_class_name = role.capitalize()
            role_class = globals().get(role_class_name)
            if role_class:
                create_kwargs = {'user': user}
                try:
                    role_class._meta.get_field('super_admin')
                    create_kwargs['super_admin'] = super_admin
                except FieldDoesNotExist:
                    pass
                role_class.objects.create(**create_kwargs)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[validate_email])
    is_email_valid = models.BooleanField(default=False)  # compte non validé, fonctionnalités inaccessibles, mail à valider
    first_name = models.CharField("Prénom", max_length=30)
    last_name = models.CharField("Nom", max_length=30)
    photo = models.FileField(upload_to="profile", null=True, blank=True)
    description = models.CharField("Présentation", max_length=255)
    role = models.CharField(
        max_length=20,
        choices=RoleEnum.choices,
        default=RoleEnum.CANDIDATE
    )
    conditions_accepted = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)  # jeton d'identification de la requête de vérification
    token_created = models.DateTimeField(null=True, blank=True) # jeton d'identification de la requête de vérification
    is_active = models.BooleanField(default=True) # compte désactivé, connexion impossible
    is_staff = models.BooleanField(default=False) # administrateur sans être super_admin (facilitateur)
    is_superuser = models.BooleanField(default=False)  # super_admin
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','role']

    def __str__(self):
        return self.email

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_groups',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        blank=True,
    )

    def token_is_valid(self):
        # Le token est valide pendant 24 heures
        if self.token_created:
            return (timezone.now() - self.token_created).days < 1
        
        return False

    def get_photo_url(self):
        if self.photo and default_storage.exists(self.photo.name):
            return self.photo.url
        return static('images/default_profile.png')

class RQTHEnum(models.TextChoices):
    DONT_SAY = 'dont_say', _('Ne souhaite pas répondre')
    WITH_RQTH = 'with_rqth', _('Avec RQTH')
    WITHOUT_RQTH = 'without_rqth', _('Sans RQTH')

class CandidateMobilityEnum(models.TextChoices):
    ON_FOOT = 'on_foot', _('À pied')
    WHEELCHAIR = 'wheelchair', _('En fauteuil roulant')
    PUBLIC_TRANSPORT = 'public_transport', _('En transports en commun')
    BICYCLE = 'bicycle', _('À vélo / trotinette')
    CAR = 'car', _('En voiture / moto')

class CandidateRemoteEnum(models.TextChoices):
    NO_PREF = 'no_pref', _('Sans préférence')
    FULL_REMOTE = 'full_remote', _('Télétravail complet')
    NO_REMOTE = 'no_remote', _('Pas de télétravail')
    HYBRID = 'hybrid', _('Hybride')

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField("Ville", max_length=50)
    country = models.CharField("Pays", max_length=50)
    job = models.CharField("Poste recherché", max_length=100)
    rqth = models.CharField("RQTH",
        max_length=20,
        choices=RQTHEnum.choices,
        blank=True,
        null=True
    )
    candidate_remote = models.CharField("Télétravail souhaité",
        max_length=20,
        choices=CandidateRemoteEnum.choices,
        blank=True,
        null=True
    )
    special_needs_comments = models.CharField("Besoins d'adaptation", max_length=255)
    attributes = models.ManyToManyField('Attribute', related_name='candidates')
    mobilities = MultiSelectField("Mobilités", choices=CandidateMobilityEnum.choices, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class ExperienceTypeEnum(models.TextChoices):
    PRO = 'pro', _('Expériences professionnelles')
    PERSONAL = 'personal', _('Activités personnelles')
    TRAINING = 'training', _('Formations')

class ExperienceContractTypeEnum(models.TextChoices):
    CDI = 'cdi', _('CDI')
    CDD = 'cdd', _('CDD')
    FREELANCE = 'freelance', _('Freelance')
    INDEPENDENT = 'independent', _('Indépendant')
    INTERNSHIP = 'internship', _('Stage')
    WORK_STUDY = 'work_study', _('Alternance')
    CIVIC_SERVICE = 'civic_service', _('Service civique')
    OTHER = 'other', _('Autre')

class WorkTimeEnum(models.TextChoices):
    FULL = 'full', _('Temps plein')
    PART = 'part', _('Temps partiel')

class Experience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='experiences')
    experience_type =  models.CharField(max_length=20, choices=ExperienceTypeEnum.choices)
    name = models.CharField("Titre", max_length=50)
    organization = models.CharField("Organisation", max_length=50)
    city = models.CharField("Ville", max_length=50, blank=True)
    country = models.CharField("Pays", max_length=50, blank=True)
    experience_contract_type = models.CharField(
        "Type de contrat",
        max_length=50,
        choices=ExperienceContractTypeEnum.choices,
        default=ExperienceContractTypeEnum.OTHER,
        null=True,
        blank=True
    )
    experience_work_time = models.CharField(
        "Temps de travail",
        max_length=50,
        choices=WorkTimeEnum.choices,
        null=True,
        blank=True
    )
    start_month = models.IntegerField("Mois de début")
    start_year = models.IntegerField("Année de début")
    end_month = models.IntegerField("Mois de fin", null=True, blank=True)
    end_year = models.IntegerField("Année de fin", null=True, blank=True)
    is_current_position = models.BooleanField("Je pratique actuellement cette activité", default=False)
    description = models.CharField("Détails", null=True, max_length=255, blank=True)
    url = models.URLField("Lien", max_length=200, blank=True)

class AttributeTypeEnum(models.TextChoices):
    SKILL = 'skill', _('Compétences')
    HOBBY = 'hobby', _('Loisirs, passions')
    CAUSE = 'cause', _('Causes, engagements')

    @classmethod
    def get_alias(cls, value):
        """Récupère l'alias en fonction de la valeur"""
        # Convertir la valeur en majuscules pour accéder à l'énumération
        value_upper = value.upper()
        return cls[value_upper].label

    @classmethod
    def get_description(cls, value):
        """Récupère la description en fonction de la valeur"""
        descriptions = {
            cls.CAUSE: _("Listez les causes qui vous importent (exemple : Aide humanitaire, Egalité des chances, La Neurodiversité…)"),
            cls.HOBBY: _("Listez les passions et loisirs que vous pratiquez (exemple : Tennis, Modélisme, Piano, ….)"),
        }
        return descriptions.get(cls(value), "")

class Attribute(models.Model):
    attribute_type = models.CharField(max_length=20, choices=AttributeTypeEnum.choices)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.get_attribute_type_display()})"

class ConditionCategory(models.TextChoices):
    TOS = 'CGU', 'Conditions Générales d\'Utilisation'
    PRIVACY = 'CONF', 'Politique de Confidentialité'
    # Ajouter d'autres catégories si nécessaire

class Condition(models.Model):
    name = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=4, choices=ConditionCategory.choices)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class JobOfferRemoteEnum(models.TextChoices):
    FULL_REMOTE = 'full_remote', _('Télétravail complet')
    NO_REMOTE = 'no_remote', _('Pas de télétravail')
    HYBRID = 'hybrid', _('Hybride')

class JobOfferContractTypeEnum(models.TextChoices):
    CDI = 'cdi', _('CDI')
    CDD = 'cdd', _('CDD')
    FREELANCE = 'freelance', _('Freelance')
    SELF_EMPLOYED = 'self_employed', _('Auto-entrepreneur')
    INTERNSHIP = 'internship', _('Stage')
    WORK_STUDY = 'work_study', _('Alternance')
    CIVIC_SERVICE = 'civic_service', _('Service civique')
    OTHER = 'other', _('Autre')

class Company(models.Model):
    name = models.CharField("Nom", max_length=200)
    description = ProseEditorField("Qui sommes-nous ?")
    diversity_and_inclusion_policy = ProseEditorField("Diversité et inclusion")
    url = models.URLField("Site Web", blank=True, null=True)

    class Meta:
        verbose_name = "entreprise"

    def __str__(self):
        return self.name

class JobOfferManager(models.Manager):
    def search_for_offers(self, session=None):
        results = self.select_related('company')
        
        if session:
            search_query = session.get('search_criteria', None)
            search_location = session.get('search_location', None)
            search_contract_type = session.get('search_contract_type', None)
            search_remote = session.get('search_remote', None)
            search_period = session.get('search_period', None)

            if search_query:
                search_query = search_query.strip()
                search_terms = re.split(',|;| ', search_query)

                for search_term in search_terms:
                    search_term = search_term.strip()
                    results = results.filter(name__icontains=search_term) | results.filter(company__name__icontains=search_term) | results.filter(skills__icontains=search_term)
            
            if search_location:
                # TODO: Make distance searches instead of just city name
                results = results.filter(city__icontains=search_location.strip())
            
            if search_contract_type:
                results = results.filter(contract_types__contains=search_contract_type)
            
            if search_remote:
                results = results.filter(remotes__contains=search_remote)
            
            if search_period:
                if search_period == JobOfferSearchPeriodsEnum.TODAY:
                    results = results.filter(publication_date=timezone.now().date())
                elif search_period == JobOfferSearchPeriodsEnum.LAST_7_DAYS:
                    results = results.filter(publication_date__gte=timezone.now().date() - timezone.timedelta(days=7))
                elif search_period == JobOfferSearchPeriodsEnum.LAST_14_DAYS:
                    results = results.filter(publication_date__gte=timezone.now().date() - timezone.timedelta(days=14))
                elif search_period == JobOfferSearchPeriodsEnum.THIS_MONTH:
                    results = results.filter(publication_date__month=timezone.now().month)
        
        return results

class JobOffer(models.Model):
    name = models.CharField("Intitulé du poste", max_length=200)
    publication_date = models.DateField("Date de mise en ligne", auto_now=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Entreprise")
    city = models.CharField("Ville", max_length=200)
    #county = models.CharField("Département", max_length=3)
    description = ProseEditorField("Descriptif du poste")
    skills = ProseEditorField("Compétences essentielles")
    job_offer_work_time = models.CharField(
        "Temps de travail",
        max_length=50,
        choices=WorkTimeEnum.choices
    )
    benefits = ProseEditorField("Avantages")
    recruitment_process = ProseEditorField("Processus de recrutement")
    contract_types = MultiSelectField("Contrat", choices=JobOfferContractTypeEnum.choices)
    remotes = MultiSelectField("Télétravail", choices=JobOfferRemoteEnum.choices)

    objects = JobOfferManager()
    
    class Meta:
        verbose_name = "offre d'emploi"
        verbose_name_plural = "offres d'emploi"
    
    def __str__(self):
        return f"{self.name} - {self.company}"

class JobOfferSearchPeriodsEnum(models.TextChoices):
    TODAY = 'today', _("Aujourd'hui")
    LAST_7_DAYS = 'last_7_days', _('7 derniers jours')
    LAST_14_DAYS = 'last_14_days', _('14 derniers jours')
    THIS_MONTH = 'this_month', _('Ce mois-ci')

class ApplicationStatusEnum(models.TextChoices):
    SAVED = 'saved', _("Sauvegardée")
    SENT = 'sent', _("Envoyée")
    EXCHANGE = 'exchange', _("Phase d'échage")
    REFUSED = 'refused', _("Candidature refusée")
    ACCEPTED = 'accepted', _("Embauché")

class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, verbose_name="Offres d'emploi")
    application_status = models.CharField(
        max_length=20,
        choices=ApplicationStatusEnum.choices,
        default=ApplicationStatusEnum.SAVED
    )
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    comments = ProseEditorField("Descriptif de la candidature", blank=True)
    application_date = models.DateField("Date de postulation", null=True, blank=True)

