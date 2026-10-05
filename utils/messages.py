from django.utils.translation import gettext_lazy as _

class ErrorMessages:
    UNIQUE = _("This field must be unique.")
    MAX_LENGTH = _("The value is too long.")
    MIN_LENGTH = _("The value is too short.")
    BLANK = _("This field may not be blank.")
    NULL = _("This field may not be null.")
    INVALID = _("Invalid value.")
    REQUIRED = _("This field is required.")
    DOES_NOT_EXIST = _("Object does not exist.")
    INCORRECT_TYPE = _("Incorrect type. Expected {data_type}.")
