from django import template

register = template.Library()

MONTHS = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
    5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
    9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}

@register.filter
def month_name(month_number):
    """Convertit un numéro de mois en nom de mois."""
    try:
        return MONTHS.get(int(month_number), "")
    except (ValueError, TypeError):
        return ""
