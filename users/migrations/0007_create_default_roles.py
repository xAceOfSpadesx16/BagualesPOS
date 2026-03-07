"""
Data migration to create default user roles (groups).

This migration creates the following roles:
- Administrador General: Full access to the system
- Gerente: Manager with broad permissions
- Administrativo: Administrative staff
- Cajero: Cashier with sales permissions
- Repositor: Stock handler
- Encargado: Branch supervisor
"""
from django.db import migrations


def create_default_roles(apps, schema_editor):
    """Create default user roles as Django groups."""
    Group = apps.get_model('auth', 'Group')
    
    # Define default roles
    roles = [
        'Administrador General',
        'Gerente',
        'Administrativo',
        'Cajero',
        'Repositor',
        'Encargado',
    ]
    
    # Create each role if it doesn't exist
    for role_name in roles:
        Group.objects.get_or_create(name=role_name)


def reverse_roles(apps, schema_editor):
    """Remove default roles if migration is reversed."""
    Group = apps.get_model('auth', 'Group')
    
    roles = [
        'Administrador General',
        'Gerente',
        'Administrativo',
        'Cajero',
        'Repositor',
        'Encargado',
    ]
    
    Group.objects.filter(name__in=roles).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0006_customuser_company_alter_customuser_branch'),
        ('auth', '__latest__'),  # Ensure auth.Group model is available
    ]

    operations = [
        migrations.RunPython(create_default_roles, reverse_roles),
    ]
