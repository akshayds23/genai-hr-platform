# app/auth.py
from flask_security.utils import hash_password
from app.models.models import db
from app.api.utils import set_user_roles


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
    hr_email = cfg.get('hr.email')
    hr_username = cfg.get('hr.username')
    hr_password = cfg.get('hr.password')

    create_default = cfg.get('hr.create_default', False)

    if not create_default or not hr_email:
        if hr_email:
            existing = user_datastore.find_user(email=hr_email)
            if existing:
                db.session.delete(existing)
        return

    if not user_datastore.find_user(email=hr_email):
        # Optional additional profile fields for hr
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
        
        print(f"HR user created: {hr_username}")


def _create_manager_user(user_datastore, cfg):
    """Create manager user (admin) if not exists"""
    manager_email = cfg.get('manager.email')
    manager_username = cfg.get('manager.username')
    manager_password = cfg.get('manager.password')

    create_default = cfg.get('manager.create_default', False)

    if not create_default or not manager_email:
        return

    if not user_datastore.find_user(email=manager_email):
        # Optional additional profile fields for manager
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
        
        print(f"Manager user created: {manager_username}")

def _create_employee_user(user_datastore, cfg):
    """Create employee user if not exists"""
    employee_email = cfg.get('employee.email')
    employee_username = cfg.get('employee.username')
    employee_password = cfg.get('employee.password')

    create_default = cfg.get('employee.create_default', False)

    if not create_default or not employee_email:
        return

    if not user_datastore.find_user(email=employee_email):
        # Optional additional profile fields for employee
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
        
        print(f"Employee user created: {employee_username}")