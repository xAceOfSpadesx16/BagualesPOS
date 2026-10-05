from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .messages import ErrorMessages

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # If the exception is a ValidationError (DRF or Django), standardize the messages
        if isinstance(exc, (ValidationError, DjangoValidationError)):
            response.data = _standardize_errors(response.data)

    return response

def _standardize_errors(data):
    """
    Recursively traverse the error data and replace messages based on error codes.
    """
    if isinstance(data, dict):
        return {k: _standardize_errors(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_standardize_errors(item) for item in data]
    elif isinstance(data, str):
        # If it's a simple string, we can't easily check the code unless we have the ErrorDetail object.
        # However, DRF usually returns ErrorDetail objects which behave like strings but have a .code attribute.
        return _replace_message(data)
    return data

def _replace_message(error_detail):
    """
    Replace the error message if the code matches a standard one.
    """
    # Check if it has a 'code' attribute (it should be an ErrorDetail object)
    code = getattr(error_detail, 'code', None)
    
    if code == 'unique':
        return ErrorMessages.UNIQUE
    elif code == 'max_length':
        return ErrorMessages.MAX_LENGTH
    elif code == 'min_length':
        return ErrorMessages.MIN_LENGTH
    elif code == 'blank':
        return ErrorMessages.BLANK
    elif code == 'null':
        return ErrorMessages.NULL
    elif code == 'required':
        return ErrorMessages.REQUIRED
    elif code == 'invalid':
        return ErrorMessages.INVALID
    elif code == 'does_not_exist':
        return ErrorMessages.DOES_NOT_EXIST
    elif code == 'incorrect_type':
        return ErrorMessages.INCORRECT_TYPE
    
    return error_detail
