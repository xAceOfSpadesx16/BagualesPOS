from __future__ import annotations
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.db.models import Model, CASCADE
from django.db.models.fields import CharField, EmailField, DateTimeField
from django.db.models.fields.related import OneToOneField

from utils import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario debe ser proporcionado')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractUser):
    profile: Profile
    email = EmailField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Profile(Model):
    user = OneToOneField(get_user_model(), on_delete=CASCADE, related_name='profile')
    phone_number = PhoneNumberField(null=True, blank=True)
    dni = CharField(max_length=9, null=True, blank=True, unique=True)
    address = CharField(max_length=100, null=True, blank=True)
    city = CharField(max_length=50, null=True, blank=True)
    province = CharField(max_length=50, null=True, blank=True)
    postal_code = CharField(max_length=10, null=True, blank=True)
    country = CharField(max_length=50, null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'