# app/auth.py
from flask_security.utils import hash_password

from app.api.utils import set_user_roles
from app.models.models import db


def create_default_roles_and_admin(user_datastore, cfg):
    """Create default roles and admin users if they don't exist"""

    # Create roles if they don't exist
    _create_default_roles(user_datastore)

    # Create admin users if they don't exist
    _create_hr_user(user_datastore, cfg)
    _create_manager_user(user_datastore, cfg)
    _create_employee_user(user_datastore, cfg)

    db.session.commit()


def _create_default_roles(user_datastore):
    """Create default user roles"""
    roles = [
        ("hr", "Super Administrator"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    ]

    for role_name, role_description in roles:
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name, description=role_description)


def _create_hr_user(user_datastore, cfg):
    """Create HR user (super admin) if not exists"""
    hr_email = cfg.get('hr.email', 'hr@example.com')
    hr_username = cfg.get('hr.username', 'hr')
    hr_password = cfg.get('hr.password', 'hr123')

    create_default = cfg.get('hr.create_default', True)

    if not create_default or not hr_email:
        return

    if not user_datastore.find_user(email=hr_email):
        hr_kwargs = {
            'email': hr_email,
            'username': hr_username,
            'password': hash_password(hr_password)
        }

        for key in ('first_name', 'last_name', 'phone', 'address', 'organization'):
            cfg_key = f'hr.{key}'
            if cfg.get(cfg_key):
                hr_kwargs[key] = cfg.get(cfg_key)

        hr_user = user_datastore.create_user(**hr_kwargs)
        set_user_roles(hr_user, ['hr'])


def _create_manager_user(user_datastore, cfg):
    """Create manager user (admin) if not exists"""
    manager_email = cfg.get('manager.email', 'manager@example.com')
    manager_username = cfg.get('manager.username', 'manager')
    manager_password = cfg.get('manager.password', 'manager123')

    create_default = cfg.get('manager.create_default', True)

    if not create_default or not manager_email:
        return

    if not user_datastore.find_user(email=manager_email):
        manager_kwargs = {
            'email': manager_email,
            'username': manager_username,
            'password': hash_password(manager_password)
        }

        for key in ('first_name', 'last_name', 'phone', 'address', 'organization'):
            cfg_key = f'manager.{key}'
            if cfg.get(cfg_key):
                manager_kwargs[key] = cfg.get(cfg_key)

        manager_user = user_datastore.create_user(**manager_kwargs)
        set_user_roles(manager_user, ['manager'])


def _create_employee_user(user_datastore, cfg):
    """Create employee user if not exists"""
    employee_email = cfg.get('employee.email', 'employee@example.com')
    employee_username = cfg.get('employee.username', 'employee')
    employee_password = cfg.get('employee.password', 'employee123')

    create_default = cfg.get('employee.create_default', True)

    if not create_default or not employee_email:
        return

    if not user_datastore.find_user(email=employee_email):
        employee_kwargs = {
            'email': employee_email,
            'username': employee_username,
            'password': hash_password(employee_password)
        }

        for key in ('first_name', 'last_name', 'phone', 'address', 'organization'):
            cfg_key = f'employee.{key}'
            if cfg.get(cfg_key):
                employee_kwargs[key] = cfg.get(cfg_key)

        employee_user = user_datastore.create_user(**employee_kwargs)
        set_user_roles(employee_user, ['employee'])
