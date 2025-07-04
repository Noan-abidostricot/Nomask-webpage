import pytest
from apps.neuroa_app.models import User
from apps.neuroa_app.backend import CustomAuthBackend


@pytest.mark.django_db
class TestCustomAuthBackend:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="test@example.com",
            password="StrongPassword123!",
            first_name="Test",
            role="candidate",
            conditions_accepted=True,
        )

    def test_custom_auth_backend(self, user):
        backend = CustomAuthBackend()

        authenticated_user = backend.authenticate(None, email='test@example.com', password='StrongPassword123!')
        assert authenticated_user is not None
        assert authenticated_user.email == 'test@example.com'

        failed_auth = backend.authenticate(None, email='test@example.com', password='WrongPassword123!')
        assert failed_auth is None

        non_existent = backend.authenticate(None, email='nonexistent@example.com', password='SomePassword123!')
        assert non_existent is None

        retrieved_user = backend.get_user(user.id)
        assert retrieved_user == user

        non_existent_user = backend.get_user(999999)
        assert non_existent_user is None
