from django.test import TestCase
from apps.neuroa_app.forms import SignUpForm, UserProfileForm, CandidateProfileForm, ExperienceForm, AttributeForm
from apps.neuroa_app.models import RoleEnum


def test_signup_form_valid():
    form_data = {
        'first_name': 'Test',
        'last_name' : 'Test',
        'email': 'test@example.com',
        'password': 'StrongPassword123!',
        'role': RoleEnum.CANDIDATE.value,
        'conditions_accepted': True,
    }
    form = SignUpForm(data=form_data)
    assert form.is_valid()

def test_signup_form_invalid():
    form_data = {
        'first_name': 'Test',
        'last_name': 'Test',
        'email': 'invalid_email',
        'password': 'StrongPassword123!',
        'conditions_accepted': False,
    }
    form = SignUpForm(data=form_data)
    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'conditions_accepted' in form.errors

def test_signup_form_missing_fields():
    form_data = {
        'first_name': 'Test',
        'last_name': 'Test',
    }
    form = SignUpForm(data=form_data)
    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'password' in form.errors
    assert 'conditions_accepted' in form.errors

class TestUserProfileForm(TestCase):
    def test_user_profile_form_valid(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'description': 'Test description'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

class TestCandidateProfileForm(TestCase):
    def test_candidate_profile_form_valid(self):
        form_data = {
            'city': 'Test City',
            'country': 'Test Country',
            'job': 'Test Job',
            'rqth': 'dont_say',
            'candidate_remote': 'no_pref',
            'special_needs_comments': 'Test comments'
        }
        form = CandidateProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

class TestExperienceForm(TestCase):
    def test_experience_form_valid(self):
        form_data = {
            'experience_type': 'pro',
            'organization': 'Test Org',
            'name': 'Test Experience',
            'city': 'Test City',
            'country': 'Test Country',
            'experience_contract_type': 'contract',
            'experience_work_time': 'full',
            'start_year': 2000,
            'start_mouth': 12,
            'is_current_position': True
        }
        form = ExperienceForm(data=form_data)
        self.assertTrue(form.is_valid())

class TestAttributeForm(TestCase):
    def test_attribute_form_valid(self):
        form_data = {
            'attribute_type': 'skill',
            'name': 'Test Skill'
        }
        form = AttributeForm(data=form_data)
        self.assertTrue(form.is_valid())
