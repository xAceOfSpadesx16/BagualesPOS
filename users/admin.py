from django.contrib import admin
from users.models import Profile
from django.contrib.auth import get_user_model


admin.site.register(Profile)
admin.site.register(get_user_model())
