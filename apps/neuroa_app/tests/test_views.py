import uuid
import pytest
from django.urls import reverse
from apps.neuroa_app.models import Candidate, User, Condition, RoleEnum, Experience, Attribute
from apps.neuroa_app.password_validation import CustomPasswordValidator
from django.test import TestCase, Client
from unittest.mock import patch
import json

from django.conf import settings


class CsrfEnforcedClient(Client):
    def __init__(self, **defaults):
        super().__init__(enforce_csrf_checks=True, **defaults)

@pytest.fixture
def client():
    return CsrfEnforcedClient()

def get_unique_email():
    return f"test_{uuid.uuid4()}@example.com"

def test_get_csrf_token(client):
    response = client.get(reverse('get_csrf_token'))
    assert response.status_code == 200
    assert 'csrfToken' in json.loads(response.content)

@pytest.mark.django_db
class TestSignUpCandidateView:
    def get_csrf_token(self, client):
        csrf_url = reverse('get_csrf_token')
        csrf_response = client.get(csrf_url)
        return csrf_response.json()['csrfToken']

    def test_signup_view_weak_password(self, client):
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        validator = CustomPasswordValidator(min_length=10)

        weak_passwords = [
            ("Sh0rt", f"Le mot de passe doit contenir au moins {validator.min_length} caractères."),
            ("longpasswordnoupper123", "Le mot de passe doit contenir au moins une majuscule."),
            ("LONGPASSWORDNOLOWER123", "Le mot de passe doit contenir au moins une minuscule."),
            ("LongPasswordNoNumber", "Le mot de passe doit contenir au moins un chiffre."),
        ]

        for password, expected_error in weak_passwords:
            data = {
                'first_name': 'Test',
                'last_name': 'Test',
                'email': get_unique_email(),
                'password': password,
                'conditions_accepted': True
            }

            response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

            assert response.status_code == 400
            response_data = json.loads(response.content)
            assert response_data['success'] == False
            assert expected_error in response_data['errors']['password']

    def test_signup_post_success(self, client):
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': get_unique_email(),
            'password': 'StrongPassword123!',
            'conditions_accepted': True
        }

        response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

        assert response.status_code == 201
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.email == data['email']
        assert user.conditions_accepted == True
        assert Candidate.objects.filter(user=user).exists()

    def test_signup_post_invalid_email(self, client):
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': 'invalid_email',
            'password': 'StrongPassword123!',
            'conditions_accepted': True
        }

        response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['success'] == False
        assert 'email' in response_data['errors']
        assert 'Saisissez une adresse e-mail valide.' in response_data['errors']['email']

    def test_signup_post_missing_terms(self, client):
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': get_unique_email(),
            'password': 'StrongPassword123!',
            'conditions_accepted': False
        }

        response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['errors'][0] == "L'utilisateur doit approuver les conditions"

    @patch('os.getenv')
    def test_signup_with_email_server(self, mock_getenv, client):
        mock_getenv.return_value = 'test@example.com'
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': get_unique_email(),
            'password': 'StrongPassword123!',
            'conditions_accepted': True
        }

        response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

        assert response.status_code == 201
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert response_data['email'] == data['email']
        assert "Nous vous avons envoyé un mail à l'adresse ci-dessus Veuillez cliquer sur le lien se trouvant dans ce mail pour valider votre compte." in response_data['message']

    @patch('os.getenv')
    def test_signup_without_email_server(self, mock_getenv, client):
        mock_getenv.return_value = None
        url = reverse('sign_up')
        csrf_token = self.get_csrf_token(client)
        data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': get_unique_email(),
            'password': 'StrongPassword123!',
            'conditions_accepted': True
        }

        response = client.post(url, data=data, HTTP_X_CSRFTOKEN=csrf_token)

        assert response.status_code == 201
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert response_data['email'] == data['email']
        assert "Validation par e-mail actuellement indisponible" in response_data['message']

@pytest.mark.django_db
def test_condition_view(client):
    Condition.objects.create(name='Test Condition', body='Test Body', category='CGU')
    response = client.get(reverse('condition'))
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Condition'

def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200

@pytest.mark.django_db
class TestLoginView:
    @pytest.fixture
    def client(self):
        return Client()

    @pytest.fixture
    def user(self):
        user = User.objects.create_user(
            email=get_unique_email(),
            password="StrongPassword123!",
            first_name="Test",
            last_name="Test",
            role=RoleEnum.CANDIDATE.value,
            conditions_accepted=True,
        )

        user.is_email_valid = True
        user.save()
        return user

    def test_login_successful(self, client, user):
        response = client.post(reverse('login'), {
            'email': user.email,
            'password': 'StrongPassword123!',
        })
        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json()['message'] == "Connexion réussie"

    def test_login_email_not_validated(self, client, user):
        user.is_email_valid = False
        user.save()
        response = client.post(reverse('login'), {
            'email': user.email,
            'password': 'StrongPassword123!',
        })
        assert response.status_code == 200
        assert response.json()['success'] == False
        assert "Vous n'avez pas confirmé votre adresse email" in response.json()['message']

    def test_login_failed_wrong_password(self, client, user):
        response = client.post(reverse('login'), {
            'email': user.email,
            'password': 'WrongPassword123!',
        })
        assert response.status_code == 400
        assert response.json()['success'] == False
        assert response.json()['message'] == "Identifiants invalides"

    def test_login_failed_non_existent_user(self, client):
        response = client.post(reverse('login'), {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!',
        })
        assert response.status_code == 400
        assert response.json()['success'] == False
        assert response.json()['message'] == "Identifiants invalides"

    def test_login_remember_me(self, client, user):
        response = client.post(reverse('login'), {
            'email': user.email,
            'password': 'StrongPassword123!',
            'rememberMe': 'on',
        })
        assert response.status_code == 200
        assert response.json()['success'] == True
        assert client.session.get_expiry_age() > 30000000  # Vérifier que la durée est très longue (plus de 347 jours)

    def test_login_without_remember_me(self, client, user):
        response = client.post(reverse('login'), {
            'email': user.email,
            'password': 'StrongPassword123!',
        })
        assert response.status_code == 200
        assert response.json()['success'] == True
        assert client.session.get_expire_at_browser_close() == True

class TestProfileView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=get_unique_email(),
            password='StrongPassword123!',
            first_name='Test',
            last_name='User',
            role='candidate',
            conditions_accepted=True
        )
        self.candidate, _ = Candidate.objects.get_or_create(user=self.user)
        self.profile_url = reverse('profile')

    def test_profile_view_authenticated(self):
        self.client.login(email=self.user.email, password='StrongPassword123!')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

class TestUpdateProfileView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=get_unique_email(),
            password='StrongPassword123!',
            first_name='Test',
            last_name='User',
            role='candidate',
            conditions_accepted=True
        )
        self.candidate, _ = Candidate.objects.get_or_create(user=self.user)
        self.update_profile_url = reverse('update_profile')

    def test_update_profile(self):
        self.client.login(email=self.user.email, password='StrongPassword123!')
        data = {
            'action': 'update_profile',
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': self.user.email,
            'description': 'Updated description',
            'city': 'New City',
            'country': 'New Country',
            'job': 'New Job',
            'rqth': 'dont_say',
            'candidate_remote': 'no_pref',
            'special_needs_comments': 'Updated comments'
        }
        response = self.client.post(self.update_profile_url, data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        if response_data['status'] == 'error':
            print("Erreurs de mise à jour du profil:", response_data.get('errors'))
        self.assertEqual(response_data['status'], 'success')
        self.user.refresh_from_db()
        self.candidate.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.candidate.city, 'New City')

    def test_add_experience(self):
        self.client.login(email=self.user.email, password='StrongPassword123!')
        data = {
            'action': 'add_experience',
            'experience_type': 'pro',
            'organization': 'Test Org',
            'name': 'Test Experience',
            'city': 'Test City',
            'country': 'Test Country',
            'start_year': 2000,
            'start_month': 12,
            'end_year': 2020,
            'end_month': 12,
            'is_current_position': False,
            'experience_contract_type': 'contract',
            'experience_work_time': 'full',
        }
        response = self.client.post(self.update_profile_url, data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        if response_data['status'] == 'error':
            print("Erreurs d'ajout d'expérience:", response_data.get('errors'))
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(Experience.objects.filter(candidate=self.candidate, name='Test Experience').exists())

    def test_add_attribute(self):
        self.client.login(email=self.user.email, password='StrongPassword123!')
        data = {
            'action': 'add_attribute',
            'attribute_type': 'skill',
            'name': 'Test Skill',
        }
        response = self.client.post(self.update_profile_url, data)
        self.assertEqual(response.status_code, 200)

        # Vérifier que l'attribut a été créé
        self.assertTrue(Attribute.objects.filter(name='Test Skill').exists())

        # Vérifier que l'attribut a été associé au candidat
        attribute = Attribute.objects.get(name='Test Skill')
        self.assertTrue(self.candidate.attributes.filter(id=attribute.id).exists())
