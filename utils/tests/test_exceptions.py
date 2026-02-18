from django.test import TestCase
from rest_framework.exceptions import ValidationError, ErrorDetail
from utils.exceptions import custom_exception_handler
from utils.messages import ErrorMessages

class CustomExceptionHandlerTestCase(TestCase):
    def test_standardize_errors_unique(self):
        exc = ValidationError({'field': [ErrorDetail(string='Unique constraint failed', code='unique')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.UNIQUE)

    def test_standardize_errors_max_length(self):
        exc = ValidationError({'field': [ErrorDetail(string='Ensure this field has no more than 10 characters.', code='max_length')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.MAX_LENGTH)

    def test_standardize_errors_blank(self):
        exc = ValidationError({'field': [ErrorDetail(string='This field may not be blank.', code='blank')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.BLANK)

    def test_standardize_errors_nested(self):
        exc = ValidationError({
            'nested': {
                'field': [ErrorDetail(string='This field is required.', code='required')]
            }
        })
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['nested']['field'][0], ErrorMessages.REQUIRED)
    
    def test_standardize_errors_min_length(self):
        exc = ValidationError({'field': [ErrorDetail(string='Ensure this field has at least 3 characters.', code='min_length')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.MIN_LENGTH)
        
    def test_standardize_errors_null(self):
        exc = ValidationError({'field': [ErrorDetail(string='This field may not be null.', code='null')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.NULL)

    def test_standardize_errors_invalid(self):
        exc = ValidationError({'field': [ErrorDetail(string='Invalid value.', code='invalid')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.INVALID)
        
    def test_standardize_errors_does_not_exist(self):
        # DoesNotExist usually comes from Django models, but DRF might wrap it or return specific code
        exc = ValidationError({'field': [ErrorDetail(string='Object does not exist.', code='does_not_exist')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.DOES_NOT_EXIST)

    def test_standardize_errors_incorrect_type(self):
        exc = ValidationError({'field': [ErrorDetail(string='Incorrect type.', code='incorrect_type')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], ErrorMessages.INCORRECT_TYPE)
        
    def test_standardize_errors_unknown_code(self):
        # Should remain unchanged
        exc = ValidationError({'field': [ErrorDetail(string='Custom Error', code='custom')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], 'Custom Error')

    def test_standardize_errors_string_only(self):
        # Case where it's a simple string, not ErrorDetail with code
        # DRF ValidationError(list) converts strings to ErrorDetail(string, code='invalid') by default!
        # We must explicitly provide ErrorDetail with code=None or 'custom' to test fallback.
        exc = ValidationError({'field': [ErrorDetail('Simple string error', code='custom')]})
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data['field'][0], 'Simple string error')

    def test_standardize_errors_list(self):
         # Test processing a list directly (not in dict)
        exc = ValidationError([ErrorDetail(string='Invalid.', code='invalid')])
        response = custom_exception_handler(exc, None)
        self.assertEqual(response.data[0], ErrorMessages.INVALID)

    def test_standardize_errors_other_types(self):
        # Test input that is not dict, list, or str (e.g. None or int) - verifies implicit return data
        # _standardize_errors is recursive.
        from utils.exceptions import _standardize_errors
        self.assertIsNone(_standardize_errors(None))
        self.assertEqual(_standardize_errors(123), 123)
