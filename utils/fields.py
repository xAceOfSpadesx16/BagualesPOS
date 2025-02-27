from django.db.models import CharField
from django.core.validators import RegexValidator

class PhoneNumberField(CharField):
    """
    Custom field for phone numbers with a regex validator
    """
    def __init__(self, max_length=20, *args, **kwargs):
        kwargs['max_length'] = max_length
        kwargs['validators'] = [
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="El número de teléfono debe estar en el formato: '+999999999'. Máximo 20 dígitos."
            )
        ]
        super().__init__(*args, **kwargs)