from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def __init__(self, min_length=10):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Le mot de passe doit contenir au moins {self.min_length} caractères.",
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une majuscule.",
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une minuscule.",
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un chiffre.",
                code='password_no_digit',
            )

    def get_help_text(self):
        return f"""
        Votre mot de passe doit contenir au moins {self.min_length} caractères,
        inclure au moins une majuscule, une minuscule et un chiffre.
        """
