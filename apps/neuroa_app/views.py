from datetime import datetime
from smtplib import SMTPException

from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.db.models import Case, When
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.urls import reverse

from .forms import SignUpForm
from .models import *
from .forms import UserProfileForm, CandidateProfileForm, ExperienceForm, AttributeForm, BasicInfoForm, CandidateInfoForm, EXPERIENCE_TYPE_INFOS

import logging
import json
import uuid
import os

logger = logging.getLogger(__name__)

#CSRF

@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

# SSR controllers

@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SignUpCandidateView(View):
    def get(self, request):
        form = SignUpForm()
        conditions = Condition.objects.all().order_by('category')
        return render(request, 'signup_modal.html', {'form': form, 'conditions': conditions})

    def post(self, request):
        if not request.POST.get('email'):
            return JsonResponse(
                {"errors": ["L'adresse email est obligatoire"]},
                status=400
            )

        if User.objects.filter(email=request.POST.get('email')).exists():
            return JsonResponse(
                {"errors": ["Un utilisateur avec cette adresse e-mail existe déjà."]},
                status=400
            )

        mutable_data = dict(request.POST.items())

        mutable_data['role'] = RoleEnum.CANDIDATE.value

        mutable_data['conditions_accepted'] = str(mutable_data.get('conditions_accepted')).lower() == 'on' or str(
            mutable_data.get('conditions_accepted')).lower() == 'true' or mutable_data.get(
            'conditions_accepted') is True

        if not mutable_data['conditions_accepted']:
            return JsonResponse(
                {"errors": ["L'utilisateur doit approuver les conditions"]},
                status=400
            )

        form = SignUpForm(data=mutable_data)

        if form.is_valid():
            try:
                # Créer l'utilisateur mais ne pas l'enregistrer encore
                user = User(
                    email=form.cleaned_data['email'],
                )
                user.set_password(form.cleaned_data['password'])
                # Envoyer l'email de validation
                mail_status = send_validation_mail_util(request=request, user=user)
                if mail_status['success']:
                    return JsonResponse({
                        "success": True,
                        "email": user.email,
                        "message": mail_status['message']
                    }, status=201)
                else:
                    # Retourner une erreur si l'envoi de l'email échoue
                    logger.error(f"Échec de l'envoi de l'email de validation : {mail_status['message']}")
                    return JsonResponse({
                        "success": False,
                        "errors": {"email": mail_status['message']}
                    }, status=500)
            except ValidationError as e:
                logger.error(f"Erreur de validation : {e.messages}")
                return JsonResponse({
                    "success": False,
                    "errors": {"password": e.messages}
                }, status=400)
        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)

class ConditionView(View):
    def get(self, request):
        conditions = Condition.objects.all().order_by('category')
        if conditions.exists():
            return JsonResponse([{
                'id': condition.id,
                'name': condition.name,
                'body': condition.body,
                'category': condition.category,
                'category_name': condition.get_category_display()
            } for condition in conditions], safe=False)
        else:
            return JsonResponse([{
                'id': None,
                'name': '',
                'body': '',
                'category': '',
                'category_name': ''
            }], safe=False)

def send_validation_mail_util(request, user):
    if not os.getenv('EMAIL_HOST_USER'):
        user.save()
        return {
            'success': False,
            'message': "Validation par e-mail actuellement indisponible. Nous avons enrigistré votre compte, vous pourrez le valider plus tard"
        }
    else:
        try:
            # Générer un nouveau UUID pour le token
            token = uuid.uuid4()

            # Sauvegarder le token dans le champ de l'utilisateur
            user.token = token
            user.token_created = timezone.now()

            # Créer l'URL de validation
            validation_url = request.build_absolute_uri(
                reverse('validate_email', args=[str(token)])
            )
            html_message = render_to_string('email_content.html', {'validation_url': validation_url})
            send_mail(
                'Validez votre compte NoMask',
                f"Bienvenue sur NoMask !\n\nPour finaliser la création de votre compte et avoir accès gratuitement à nos offres d’emplois, cliquez sur le lien ci-dessous, valable 24h :\n\n{validation_url}\n\nSi cela ne fonctionne pas, copiez ce lien et collez-le dans la barre d'adresse de votre navigateur web.\n\nMerci et à bientôt !\n\nL'équipe NoMask\n",
                os.getenv('EMAIL_HOST_USER'),
                [user.email],
                fail_silently=False,
                html_message=html_message
            )

            user.save()

            return {
                'success': True,
                'message': "Nous vous avons envoyé un mail à l'adresse ci-dessus Veuillez cliquer sur le lien se trouvant dans ce mail pour valider votre compte."
            }
        except ValidationError as e:
            logger.error(f"Erreur de validation lors de la création du token : {str(e)}")
            return {
                'success': False,
                'message': "Une erreur est survenue lors de la création du token de validation."
            }
        except SMTPException as e:
            logger.error(f"Erreur SMTP lors de l'envoi de l'email : {str(e)}")
            return {
                'success': False,
                'message': "Une erreur est survenue lors de l'envoi de l'email de validation."
            }
        except Exception as e:
            logger.error(f"Erreur inattendue : {str(e)}")
            return {
                'success': False,
                'message': "Une erreur inattendue est survenue. Veuillez réessayer plus tard."
            }

@require_POST
@csrf_protect
def send_validation_mail(request):
    data = json.loads(request.body.decode('utf-8'))
    email = data.get('email')
    if not os.getenv('EMAIL_HOST_USER'):
        return JsonResponse({
            "success": False,
            "message": "Validation par e-mail actuellement indisponible",
            "email": email
        })
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Utilisateur non trouvé."
        }, status=400)

    mail_status = send_validation_mail_util(request, user)

    return JsonResponse({
        "success": mail_status['success'],
        "message": mail_status['message'],
        "email": user.email
    })

def validate_email(request, token):
    try:
        user = get_object_or_404(User, token=token)

        if user.token:
            user.is_email_valid = True
            user.token = None  # Effacer le token après utilisation
            user.save()

            return render(request, 'email_validation_success.html', {'email': user.email})
        else:
            return render(request, 'email_token_invalid.html')
    except Exception:
        return render(request, 'email_token_invalid.html')

@require_POST
@csrf_protect
def login_view(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    remember_me = request.POST.get('rememberMe') == 'on'

    user = authenticate(request, email=email, password=password)

    if user is not None:
        if user.is_email_valid:
            auth_login(request, user)
            if remember_me:
                request.session.set_expiry(365 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)
            return JsonResponse({
                "success": True,
                "message": "Connexion réussie"
            })
        else:
            mail_status = send_validation_mail_util(request=request, user=user)
            if mail_status['success']:
                return JsonResponse({
                    "success": False,
                    "email": user.email,
                    "unverified_mail": True,
                    "message": mail_status['message']
                })
            else:
                # Retourner une erreur si l'envoi de l'email échoue
                logger.error(f"Échec de l'envoi de l'email de validation : {mail_status['message']}")
                return JsonResponse({
                    "success": False,
                    "mail_resend_fail": True,
                    "email": user.email,
                    "unverified_mail": True,
                    "message": mail_status['message']
                })
    else:
        return JsonResponse({
            "success": False,
            "message": "Identifiants invalides"
        }, status=400)

@login_required
@require_GET
def get_experience_data(request, experience_id):
    experience = Experience.objects.filter(id=experience_id, candidate=request.user.candidate).first()
    if experience:
        data = {
            'id': experience.id,
            'experience_type': experience.experience_type,
            'organization': experience.organization,
            'name': experience.name,
            'city': experience.city,
            'country': experience.country,
            'experience_contract_type': experience.experience_contract_type,
            'experience_work_time': experience.experience_work_time,
            'start_month': experience.start_month,
            'start_year': experience.start_year,
            'end_month': experience.end_month,
            'end_year': experience.end_year,
            'is_current_position': experience.is_current_position,
            'description':experience.description,
            'url': experience.url,
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Experience not found'}, status=404)

@login_required
@require_GET
def get_attribute_data(request, attribute_id):
    attribute = Attribute.objects.filter(id=attribute_id).first()
    if attribute:
        data = {
            'id': attribute.id,
            'attribute_type': attribute.attribute_type,
            'name': attribute.name,
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Attribute not found'}, status=404)

@csrf_exempt
@require_POST
@login_required
def update_profile(request):

    user = request.user
    candidate = user.candidate

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            if field in ['first_name', 'last_name', 'description']:
                setattr(user, field, value)
                user.save()
            elif field in ['city', 'country', 'job', 'special_needs_comments']:
                setattr(candidate, field, value)
                candidate.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'Champ inconnu'})

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        action = request.POST.get('action')

        if action == 'update_basic_info':
            form = BasicInfoForm(request.POST, user=user, candidate=candidate)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expérience enregistrée avec succès'
                })
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})

        elif action == 'update_candidate_info':
            form = CandidateInfoForm(request.POST, candidate=candidate)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expérience enregistrée avec succès'
                })
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})

        elif action == 'update_profile':
            user_form = UserProfileForm(request.POST, instance=request.user)
            candidate_form = CandidateProfileForm(request.POST, instance=request.user.candidate)
            if user_form.is_valid() and candidate_form.is_valid():
                user_form.save()
                candidate_form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expérience enregistrée avec succès'
                })
            else:
                errors = user_form.errors.update(candidate_form.errors)
                return JsonResponse({'status': 'error', 'errors': errors})

        elif action == 'add_experience':
            experience_form = ExperienceForm(request.POST)
            experience_type = request.POST.get('experience_type')

            experience_form.data = experience_form.data.copy()
            experience_form.data['experience_type'] = experience_type

            if experience_form.is_valid():
                experience = experience_form.save(commit=False)
                experience.candidate = candidate
                experience.experience_type = experience_type
                experience.save()

                return JsonResponse({
                    'status': 'success',
                    'experience': {
                        'name': experience.name,
                        'experience_type': experience.experience_type,
                        'experience_type_display': experience.get_experience_type_display(),
                        'organization': experience.organization,
                        'city': experience.city,
                        'country': experience.country,
                        'experience_contract_type': experience.experience_contract_type,
                        'experience_contract_type_display': experience.get_experience_contract_type_display(),
                        'experience_work_time': experience.experience_work_time,
                        'start_month': experience.start_month if experience.start_month else None,
                        'start_year': experience.start_year if experience.start_year else None,
                        'end_month': experience.end_month if experience.end_month else None,
                        'end_year': experience.end_year if experience.end_year else None,
                        'is_current_position': experience.is_current_position,
                    }
                })
            else:
                return JsonResponse({'status': 'error', 'errors': experience_form.errors})

        elif action == 'add_attribute':
            raw_data = request.POST.copy()
            attribute_type = raw_data.get('attribute_type')
            raw_names = [n.strip() for n in raw_data.get('name', '').split(',') if n.strip()]

            created_attributes = []
            error_messages = []
            valid_count = 0

            for raw_name in raw_names:
                # Crée un formulaire avec un seul élément
                form_data = {
                    'name': raw_name,  # Un élément unique
                    'attribute_type': attribute_type
                }

                attribute_form = AttributeForm(form_data)

                if attribute_form.is_valid():
                    name = attribute_form.cleaned_data['name'][0]
                    attribute, created = Attribute.objects.get_or_create(
                        name=name,
                        attribute_type=attribute_type,
                        defaults={'attribute_type': attribute_type}
                    )

                    if created:
                        created_attributes.append(attribute)
                        request.user.candidate.attributes.add(attribute)
                        valid_count += 1
                else:
                    # Concaténation des messages d'erreur
                    field_errors = attribute_form.errors.get('name', [])
                    error_messages.extend(f"'{raw_name}': {error}" for error in field_errors)

            if valid_count > 0 or error_messages:
                full_error_message = " | ".join(error_messages) if error_messages else ""
                response = {
                    'status': 'success' if not error_messages else 'partial_success',
                    'message': f"{valid_count} éléments ajoutés" + (
                        f" | Erreurs : {full_error_message}" if error_messages else ""),
                    'attributes': [{
                        'name': attr.name,
                        'type': attr.attribute_type
                    } for attr in created_attributes]
                }
                return JsonResponse(response)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Aucun élément valide à ajouter'
                })
        else:
            return JsonResponse({'status': 'error', 'message': "Action inconnue"})

@csrf_exempt
@require_POST
@login_required
def upload_photo(request):
    if 'photo' in request.FILES:
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        return JsonResponse({'status': 'success', 'photo_url': user.photo.url})
    return JsonResponse({'status': 'error', 'message': 'Aucune photo fournie'})

@csrf_exempt
@require_POST
@login_required
def update_experience(request):
    experience_id = request.POST.get('experience_id')
    experience = Experience.objects.filter(id=experience_id, candidate=request.user.candidate).first()
    if experience:
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Experience not found or invalid data'})

@csrf_exempt
@require_POST
@login_required
def update_attribute(request):
    attribute_id = request.POST.get('attribute_id')
    candidate = request.user.candidate
    attribute = candidate.attributes.filter(id=attribute_id).first()
    if attribute:
        attribute_form = AttributeForm(request.POST, instance=attribute)
        if attribute_form.is_valid():
            attribute_form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data', 'errors': attribute_form.errors})
    return JsonResponse({'status': 'error', 'message': 'Attribute not found'})

@csrf_exempt
@require_POST
@login_required
def delete_photo(request):
    user = request.user
    if user.photo:
        user.photo.delete()
        user.photo = None
        user.save()
    return JsonResponse({'status': 'success'})

@csrf_exempt
@require_POST
@login_required
def delete_experience(request):
    experience_id = request.POST.get('experience_id')
    experience = Experience.objects.filter(id=experience_id, candidate=request.user.candidate).first()
    if experience:
        experience.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Experience not found'})

@csrf_exempt
@require_POST
@login_required
def delete_attribute(request):
    attribute_id = request.POST.get('attribute_id')
    candidate = request.user.candidate
    attribute = candidate.attributes.filter(id=attribute_id).first()

    if attribute:
        candidate.attributes.remove(attribute)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Attribute not found'})

# Views

def home(request):
    context = {
        'page_title': 'Bienvenue sur la plateforme NoMask',
        'search_criteria': request.session.get('search_criteria', None),
        'location': request.session.get('location', None)
        }
    return render(request, 'home.html', context)

@login_required
def profile(request):
    user = User.objects.get(email=request.user)
    candidate = Candidate.objects.get(user=user)

    # Trier et grouper les expériences
    experiences = Experience.objects.filter(candidate=candidate).order_by(
        Case(*[When(experience_type=exp_type, then=pos) for pos, exp_type in enumerate(ExperienceTypeEnum.values)])
    )

    # Fonction de tri personnalisée
    def sort_experiences(exp):
        current_date = datetime.now().date()
        next_year_date = current_date.replace(year=current_date.year + 1)

        if not exp.is_current_position:
            # Expériences non actuelles
            end_year = experience.end_year if experience.end_year is not None else 0
            end_month = experience.end_month if experience.end_month is not None else 0
            return 0, end_year, end_month
        else:
            if exp.end_month is None and experience.end_year is None:
                # Expériences actuelles sans date de fin
                return 2, float('inf'), float('inf')
            else:
                end_date = datetime(exp.end_year, exp.end_month, 1).date()
                if end_date < next_year_date:
                    # Expériences avec des dates futures de moins d'un an
                    return 1, exp.end_year, exp.end_month
                else:
                    # Expériences avec des dates futures de plus d'un an
                    return 3, exp.end_year, exp.end_month

    grouped_experiences = {exp_type: [] for exp_type in ExperienceTypeEnum.values}
    for experience in experiences:
        grouped_experiences[experience.experience_type].append(experience)

    # Trier chaque groupe d'expériences
    for exp_type in grouped_experiences:
        grouped_experiences[exp_type].sort(key=sort_experiences, reverse=True)

    # Récupérer et grouper tous les attributs
    attributes = candidate.attributes.all()
    grouped_attributes = {
        AttributeTypeEnum.SKILL: attributes.filter(attribute_type=AttributeTypeEnum.SKILL),
        AttributeTypeEnum.HOBBY: attributes.filter(attribute_type=AttributeTypeEnum.HOBBY),
        AttributeTypeEnum.CAUSE: attributes.filter(attribute_type=AttributeTypeEnum.CAUSE),
    }

    attribute_types = [
        (
            attr_type.value,
            attr_type.label,
            AttributeTypeEnum.get_description(attr_type.value)
        )
        for attr_type in AttributeTypeEnum
    ]

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, request.FILES, instance=user)
            candidate_form = CandidateProfileForm(request.POST, instance=candidate)
            if user_form.is_valid() and candidate_form.is_valid():
                user_form.save()
                candidate_form.save()
                return redirect('profile')

        elif 'add_experience' in request.POST:
            experience_form = ExperienceForm(request.POST)
            experience_form.initial['experience_type'] = request.POST.get('experience_type')
            if experience_form.is_valid():
                experience = experience_form.save(commit=False)
                experience.candidate = candidate
                experience.save()
                return redirect('profile')

        elif 'add_attribute' in request.POST:
            attribute_form = AttributeForm(
                request.POST,
                attribute_type=request.POST.get('attribute_type'),
                attribute_types=attribute_types  # Passage des types avec descriptions
            )
            if attribute_form.is_valid():
                attribute = attribute_form.save()
                candidate.attributes.add(attribute)
                return redirect('profile')

        elif 'update_basic_info' in request.POST:
            basic_info_form = BasicInfoForm(request.POST, user=user, candidate=candidate)
            if basic_info_form.is_valid():
                basic_info_form.save()
                return redirect('profile')

        elif 'update_candidate_info' in request.POST:
            candidate_info_form = CandidateInfoForm(request.POST, candidate=candidate)
            if candidate_info_form.is_valid():
                candidate_info_form.save()
                return redirect('profile')

    else:
        user_form = UserProfileForm(instance=user)
        candidate_form = CandidateProfileForm(instance=candidate)
        basic_info_form = BasicInfoForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'job': candidate.job,
            'description': user.description
        }, user=user, candidate=candidate)

        candidate_info_form = CandidateInfoForm(initial={
            'city': candidate.city,
            'country': candidate.country,
            'rqth': candidate.rqth,
            'candidate_remote': candidate.candidate_remote,
            'mobilities': candidate.mobilities,
            'special_needs_comments': candidate.special_needs_comments
        }, candidate=candidate)
        experience_form = ExperienceForm()
        attribute_form = AttributeForm()

    context = {
        'user': user,
        'candidate': candidate,
        'user_form': user_form,
        'candidate_form': candidate_form,
        'basic_info_form': basic_info_form,
        'candidate_info_form': candidate_info_form,
        'experience_form': experience_form,
        'attribute_form': attribute_form,
        'grouped_experiences': grouped_experiences,
        'grouped_attributes': grouped_attributes,
        'experience_types': ExperienceTypeEnum.choices,
        'attribute_types': attribute_types,
        'experience_type_infos_json': json.dumps(EXPERIENCE_TYPE_INFOS, ensure_ascii=False),
    }
    return render(request, 'profile.html', context)

@login_required
def settings(request):
    return render(request, 'settings.html', {'page_title': 'Paramètres'})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def job_offer(request, id):
    job_offer = get_object_or_404(JobOffer, id=id)
    experiences = Experience.objects.filter(candidate=request.user.candidate)
    pro_experiences = experiences.filter(experience_type='pro')
    trainings = experiences.filter(experience_type='training')

    # Vérifier si l'offre est favorite
    is_favorite = Application.objects.filter(
        candidate=request.user.candidate,
        job_offer=job_offer,
        application_status=ApplicationStatusEnum.SAVED
    ).exists()

    # Vérifier si le candidat a déjà postulé
    has_applied = Application.objects.filter(
        candidate=request.user.candidate,
        job_offer=job_offer,
        application_status=ApplicationStatusEnum.SENT or ApplicationStatusEnum.EXCHANGE
    ).exists()

    # Vérifier si le candidat a déjà postulé
    exists = Application.objects.filter(
        candidate=request.user.candidate,
        job_offer=job_offer,
    ).exists()

    # Récupérer tous les IDs des offres favorites du candidat
    favorite_ids = Application.objects.filter(
        candidate=request.user.candidate,
        application_status=ApplicationStatusEnum.SAVED
    ).values_list('job_offer_id', flat=True)

    context = {
        'page_title': "Offre d'emploi",
        'job_offer': job_offer,
        'is_favorite': is_favorite,
        'favorite_ids': list(favorite_ids),
        'has_applied': has_applied,
        'pro_experiences': pro_experiences,
        'trainings': trainings,
    }
    return render(request, 'job_offer.html', context)

JOB_SEARCH_FIELDS = ['search_criteria', 'search_location', 'search_remote', 'search_contract_type', 'search_period']

@login_required
def job_search(request):
    if request.method == 'POST':
        for field in JOB_SEARCH_FIELDS:
            request.session[field] = request.POST.get(field, None)
        request.session['favorites_only'] = request.POST.get('favorites_only') == 'true'
    else:
        favorites_only = request.GET.get('favorites_only', 'false') == 'true'
        request.session['favorites_only'] = favorites_only

    job_offers = JobOffer.objects.search_for_offers(request.session)

    # Filtrer les offres favorites si nécessaire
    favorites_only = request.session.get('favorites_only', False)
    if favorites_only:
        favorite_ids = Application.objects.filter(
            candidate=request.user.candidate,
            application_status=ApplicationStatusEnum.SAVED
        ).values_list('job_offer_id', flat=True)
        job_offers = job_offers.filter(id__in=favorite_ids)

    # Récupérer les IDs des offres favorites pour l'affichage des icônes
    favorite_ids = Application.objects.filter(
        candidate=request.user.candidate,
        application_status=ApplicationStatusEnum.SAVED
    ).values_list('job_offer_id', flat=True)

    # Récupérer les IDs des offres auxquelles le candidat a déjà postulé
    applied_ids = Application.objects.filter(
        candidate=request.user.candidate
    ).exclude(application_status=ApplicationStatusEnum.SAVED).values_list('job_offer_id', flat=True)

    context = {
        'page_title': "Résultats de recherche",
        'job_offers': job_offers,
        'contract_types': JobOfferContractTypeEnum.choices,
        'remotes': JobOfferRemoteEnum.choices,
        'periods': JobOfferSearchPeriodsEnum.choices,
        'favorite_ids': list(favorite_ids),
        'applied_ids': list(applied_ids),
        'favorites_only': favorites_only
    }

    for field in JOB_SEARCH_FIELDS:
        context[field] = request.session.get(field, None)

    return render(request, 'job_search.html', context)

def application_monitoring(request):
    context = {'page_title': 'Suivi des candidatures',}
    return render(request, 'application_monitoring.html', context)

# PAGE EN ATTENTE
def test(request):
    context = {'page_title': 'Test',}
    return render(request, 'page-en-attente/test.html', context)

def create_job(request):
    context = {
               'page_title': 'Créer un job | NoMask',
               'recruiter' : True
              }
    
    return render(request, 'solution-recruteur/create_job.html', context)

def job_create_form(request):
    context = {
               'page_title': 'Créer une offre d\'emploi | NoMask ',
               'recruiter' : True
              }
    
    return render(request, 'solution-recruteur/job_create_form.html', context)

def gerer_mes_job_dashboard(request):
    context = {
               'page_title': 'Gérez les informations du job | NoMask ',
               'recruiter' : True
              }
    
    return render(request, 'solution-recruteur/gerer_mes_job_dashboard.html', context)

def mes_favoris(request):
    context = {
               'page_title': 'Visualisez vos favoris | NoMask ',
               'recruiter' : True
              }
    
    return render(request, 'solution-recruteur/mes_favoris.html', context)

def contact(request):
    context = {'page_title': 'Contact',}
    return render(request, 'page-en-attente/contact.html', context)

def qui_sommes_nous(request):
    context = {'page_title': 'Qui sommes nous',}
    return render(request, 'page-en-attente/qui_sommes_nous.html', context)

def error_404(request):
    context = {'page_title': 'Error 404',}
    return render(request, 'page-en-attente/error_404.html', context)

def suivi_des_candidatures(request):
    context = {'page_title': 'Suivi des candidatures',}
    return render(request, 'page-en-attente/suivi_des_candidatures.html', context)

# PAGE EN ATTENTE RECRUTEUR
def home_page_recruteur(request):
    context = {'page_title': 'Accueil recruteur',}
    return render(request, 'solution-recruteur/home_page_recruteur.html', context)

def tarifs(request):
    context = {'page_title': 'Tarifs',}
    return render(request, 'solution-recruteur/tarifs.html', context)

def prestation(request):
    context = {'page_title': 'Prestation',}
    return render(request, 'solution-recruteur/prestation.html', context)

def prestation_detaillee(request):
    context = {'page_title': 'Prestation détaillée',}
    return render(request, 'solution-recruteur/prestation_detaillee.html', context)

@login_required
@require_POST
def toggle_favorite(request, job_offer_id):
    job_offer = get_object_or_404(JobOffer, id=job_offer_id)
    candidate = request.user.candidate

    # Vérifier si une application existe déjà
    application = Application.objects.filter(candidate=candidate, job_offer=job_offer).first()

    if application:
        # Si l'application existe déjà
        if application.application_status == ApplicationStatusEnum.SAVED:
            # Si le statut est SAVED, supprimer l'entrée
            application.delete()
            is_favorite = False
        else:
            # Si le statut est différent de SAVED, ne rien faire et renvoyer le statut actuel
            is_favorite = False
    else:
        # Si l'application n'existe pas, créer une nouvelle entrée avec le statut SAVED
        Application.objects.create(candidate=candidate, job_offer=job_offer, application_status=ApplicationStatusEnum.SAVED)
        is_favorite = True

    return JsonResponse({'is_favorite': is_favorite})

@login_required
@require_POST
def submit_application(request, job_offer_id):
    job_offer = get_object_or_404(JobOffer, id=job_offer_id)
    candidate = request.user.candidate

    # Vérification du fichier PDF
    if 'resume' in request.FILES:
        uploaded_file = request.FILES['resume']
        if uploaded_file.content_type != 'application/pdf':
            return JsonResponse({
                'status': 'error',
                'message': 'Le CV doit être au format PDF'
            }, status=400)

    # Vérifier si une candidature existe déjà
    existing_application = Application.objects.filter(
        candidate=candidate,
        job_offer=job_offer
    ).first()

    try:
        if existing_application:
            # Vérifier si le statut est SENT ou EXCHANGE
            if existing_application.application_status in [ApplicationStatusEnum.SENT, ApplicationStatusEnum.EXCHANGE]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Candidature en cours.'
                }, status=400)

            # Mettre à jour la candidature existante
            existing_application.application_status = ApplicationStatusEnum.SENT
            existing_application.comments = request.POST.get('comments', '')
            existing_application.application_date = timezone.now().date()

            if 'resume' in request.FILES:
                existing_application.resume = request.FILES['resume']

            existing_application.full_clean()  # Validation du modèle
            existing_application.save()
        else:
            # Créer une nouvelle candidature
            new_application = Application(
                candidate=candidate,
                job_offer=job_offer,
                application_status=ApplicationStatusEnum.SENT,
                comments=request.POST.get('comments', ''),
                application_date=timezone.now().date()
            )

            if 'resume' in request.FILES:
                new_application.resume = request.FILES['resume']

            new_application.full_clean()  # Validation du modèle
            new_application.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Candidature envoyée avec succès.'
        })

    except ValidationError as e:
        error_messages = ' ; '.join(e.messages)
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur de validation : ' + str(error_messages)
        }, status=400)

