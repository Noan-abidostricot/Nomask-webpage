import uuid
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.neuroa_app.models import User, RoleEnum, Candidate, Experience, Attribute
from apps.neuroa_app.password_validation import CustomPasswordValidator

def get_unique_email():
    return f"test_{uuid.uuid4()}@example.com"

@pytest.mark.django_db
class TestUserModel:

    def test_create_user_with_weak_password(self):
        validator = CustomPasswordValidator(min_length=10)
        weak_passwords = [
            ("Sh0rt", f"Le mot de passe doit contenir au moins {validator.min_length} caractères."),
            ("longpasswordnoupper123", "Le mot de passe doit contenir au moins une majuscule."),
            ("LONGPASSWORDNOLOWER123", "Le mot de passe doit contenir au moins une minuscule."),
            ("LongPasswordNoNumber", "Le mot de passe doit contenir au moins un chiffre."),
        ]

        for password, expected_error in weak_passwords:
            with pytest.raises(ValidationError) as info:
                User.objects.create_user(
                    email=get_unique_email(),
                    password=password,
                    first_name="Test",
                    role=RoleEnum.CANDIDATE.value,
                    conditions_accepted=True,
                )

            # Vérifier que le message d'erreur attendu est présent dans les messages d'erreur
            error_messages = [str(err) for err in info.value.messages]
            assert expected_error in error_messages, f"Expected error '{expected_error}' not found in {error_messages}"

    def test_create_user_with_strong_password(self):
        strong_password = "StrongPassword123!"
        user = User.objects.create_user(
            email=get_unique_email(),
            password=strong_password,
            first_name="Test",
            role=RoleEnum.CANDIDATE.value,
            conditions_accepted=True,
        )
        assert user.check_password(strong_password)

    def test_create_user_without_email(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="TestPassword123!")

    def test_create_user_with_invalid_email(self):
        with pytest.raises(ValidationError):
            user = User(email="invalid_email", password="TestPassword123!")
            user.full_clean()

    def test_create_user_without_role(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="test@example.com",
                password="TestPassword123!",
                first_name="Test"
            )

class TestCandidateModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=get_unique_email(),
            password='StrongPassword123!',
            first_name='Candidate',
            last_name='Test',
            role='candidate',
            conditions_accepted=True
        )
        self.candidate, created = Candidate.objects.get_or_create(
            user=self.user,
            defaults={
                'city': 'Test City',
                'country': 'Test Country',
                'job': 'Test Job'
            }
        )

    def test_candidate_creation(self):
        self.assertTrue(isinstance(self.candidate, Candidate))
        self.assertEqual(self.candidate.user, self.user)

class TestExperienceModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=get_unique_email(),
            password='StrongPassword123!',
            first_name='Experience',
            last_name='Test',
            role='candidate',
            conditions_accepted=True
        )
        self.candidate, created = Candidate.objects.get_or_create(user=self.user)
        self.experience = Experience.objects.create(
            candidate=self.candidate,
            experience_type='pro',
            organization='Test Org',
            name='Test Experience'
        )

    def test_experience_creation(self):
        self.assertTrue(isinstance(self.experience, Experience))
        self.assertEqual(self.experience.candidate, self.candidate)

class TestAttributeModel(TestCase):
    def setUp(self):
        self.attribute = Attribute.objects.create(
            attribute_type='skill',
            name='Test Skill'
        )

    def test_attribute_creation(self):
        self.assertTrue(isinstance(self.attribute, Attribute))
        self.assertEqual(self.attribute.name, 'Test Skill')

class TestCandidateAttributeRelation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=get_unique_email(),
            password='StrongPassword123!',
            first_name='Attribute',
            last_name='Test',
            role='candidate',
            conditions_accepted=True
        )
        self.candidate, created = Candidate.objects.get_or_create(user=self.user)
        self.attribute = Attribute.objects.create(attribute_type='skill', name='Test Skill')
        self.candidate.attributes.add(self.attribute)

    def test_candidate_attribute_relation(self):
        self.assertTrue(self.attribute in self.candidate.attributes.all())
        self.assertTrue(self.candidate in self.attribute.candidates.all())

    def test_attribute_count(self):
        self.assertEqual(self.candidate.attributes.count(), 1)

    def test_remove_attribute(self):
        self.candidate.attributes.remove(self.attribute)
        self.assertEqual(self.candidate.attributes.count(), 0)