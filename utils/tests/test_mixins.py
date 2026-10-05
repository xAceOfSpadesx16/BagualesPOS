from django.test import TestCase, RequestFactory
from django.db import models
from django import forms
from django.http import HttpResponse
from unittest.mock import Mock
from utils.mixins import (
    PatchMethodMixin, FormValidationMixin, FetchRequestMixin, 
    FormGroupMixin, RequiredSuffixMixin
)

# Dummy View for testing View Mixins
class DummyView:
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse("Dispatched")

class PatchSpecifcView(PatchMethodMixin, DummyView):
    def patch(self, request, *args, **kwargs):
        return HttpResponse("Patched")

class FetchSpecificView(FetchRequestMixin, DummyView):
    pass

class FormSpecificView(FormValidationMixin, DummyView):
    def form_invalid(self, form):
        return HttpResponse("Invalid", status=200) # Base returns 200 usually


# Dummy Form for testing Form Mixins
class DummyForm(RequiredSuffixMixin, FormGroupMixin, forms.Form):
    name = forms.CharField(required=True)
    age = forms.IntegerField(required=False)

# View Mock to support super().form_invalid
class BaseFormView:
    def form_invalid(self, form):
        return HttpResponse("Error", status=200)

class FormSpecificView(FormValidationMixin, BaseFormView):
    pass

class MixinsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_patch_method_mixin(self):
        view = PatchSpecifcView()
        
        # Test PATCH
        request = self.factory.patch('/')
        response = view.dispatch(request)
        self.assertEqual(response.content, b"Patched")

        # Test POST (should fallback to dispatch -> DummyView)
        request = self.factory.post('/')
        response = view.dispatch(request)
        self.assertEqual(response.content, b"Dispatched")

    def test_patch_method_mixin_base_method(self):
        # Test the base 'patch' method that just passes
        # We need a class that inherits PatchMethodMixin but DOES NOT override patch
        class BasePatchView(PatchMethodMixin):
            pass
        
        view = BasePatchView()
        # calling patch directly should return None (implicit return of pass function)
        self.assertIsNone(view.patch(None))

    def test_fetch_request_mixin(self):
        view = FetchSpecificView()

        # Test with header
        request = self.factory.get('/', headers={'x-requested-with': 'XMLHttpRequest'})
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

        # Test without header
        request = self.factory.get('/')
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 403)

    def test_form_validation_mixin(self):
        view = FormSpecificView()
        # Mock super().form_invalid behavior by the class usage
        response = view.form_invalid(None)
        self.assertEqual(response.status_code, 422)



    def test_form_mixins(self):
        form = DummyForm()
        
        # Test RequiredSuffixMixin
        self.assertEqual(form.fields['name'].label_suffix, ' *')
        self.assertNotEqual(getattr(form.fields['age'], 'label_suffix', ''), ' *')

        # Test FormGroupMixin
        # accessing form['name'] should return a CustomBoundField
        bound_field = form['name']
        self.assertTrue(hasattr(bound_field, 'css_classes'))
        self.assertEqual(bound_field.css_classes(), "form-group")
