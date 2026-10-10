import copy
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG: dict[str, Any] = {
    'env': {
        'secret_key': 'dev-secret-key-change-in-production',
        'debug': False,
        'flask_env': 'development',
    },
    'database': {
        'url': 'sqlite:///app.db',
    },
    'security': {
        'password_salt': 'dev-password-salt-change-in-production',
        'registerable': True,
        'send_register_email': False,
        'username_enable': False,
        'username_required': False,
    },
    'hr': {
        'email': 'hr@example.com',
        'username': 'hr',
        'password': 'hr123',
        'create_default': True,
    },
    'manager': {
        'email': 'manager@example.com',
        'username': 'manager',
        'password': 'manager123',
        'create_default': True,
    },
    'employee': {
        'email': 'employee@example.com',
        'username': 'employee',
        'password': 'employee123',
        'create_default': True,
    },
    'cors': {
        'origins': [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
            "http://localhost",
            "http://127.0.0.1",
        ],
    },
}


class Configuration:
    def __init__(self, yaml_file: str | None = None):
        if yaml_file is None:
            yaml_file = str(Path(__file__).parent / "config.yaml")

        self.yaml_file = yaml_file
        self._config_data: dict[str, Any] = copy.deepcopy(DEFAULT_CONFIG)
        self._load_yaml_config()
        self._load_environment_variables()
        self._dict_to_attr(self._config_data)

    def _deep_update(self, target: dict, source: dict) -> None:
        for k, v in source.items():
            key_lower = k.lower()
            if isinstance(v, dict) and isinstance(target.get(key_lower), dict):
                self._deep_update(target[key_lower], v)
            else:
                target[key_lower] = v

    def _load_yaml_config(self) -> None:
        yaml_path = Path(self.yaml_file)
        if not yaml_path.exists():
            return

        try:
            with open(yaml_path, "r", encoding="utf-8") as stream:
                data = yaml.safe_load(stream) or {}
                if isinstance(data, dict):
                    self._deep_update(self._config_data, data)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML config: {e}")

    def _load_environment_variables(self) -> None:
        possible_env_paths = [
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
            Path.cwd() / ".env",
        ]

        for env_path in possible_env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break

        env_mapping = {
            'FLASK_ENV': 'env.flask_env',
            'SECRET_KEY': 'env.secret_key',
            'DEBUG': 'env.debug',
            'DATABASE_URL': 'database.url',
            'SECURITY_PASSWORD_SALT': 'security.password_salt',
            'SECURITY_REGISTERABLE': 'security.registerable',
            'HR_EMAIL': 'hr.email',
            'HR_PASSWORD': 'hr.password',
            'HR_USERNAME': 'hr.username',
            'MANAGER_EMAIL': 'manager.email',
            'MANAGER_PASSWORD': 'manager.password',
            'MANAGER_USERNAME': 'manager.username',
            'EMPLOYEE_EMAIL': 'employee.email',
            'EMPLOYEE_PASSWORD': 'employee.password',
            'EMPLOYEE_USERNAME': 'employee.username',
        }

        for env_var, config_path in env_mapping.items():
            val = os.getenv(env_var)
            if val is not None:
                if env_var in ('DEBUG', 'SECURITY_REGISTERABLE'):
                    val = val.lower() in ('1', 'true', 'yes')
                self._set_nested_config(config_path, val)

        cors_env = os.getenv('CORS_ORIGINS')
        if cors_env:
            origins = [o.strip() for o in cors_env.split(',') if o.strip()]
            self._set_nested_config('cors.origins', origins)

        # Normalize database URL
        db_url = self.get('database.url')
        if db_url and isinstance(db_url, str):
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
            elif db_url.startswith('postgresql://') and '+psycopg' not in db_url:
                db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
            self._set_nested_config('database.url', db_url)

    def _set_nested_config(self, path: str, value: Any) -> None:
        keys = path.lower().split('.')
        config = self._config_data

        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def _dict_to_attr(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            attr_name = key.upper()
            if isinstance(value, dict):
                namespace = type('ConfigNamespace', (), {})()
                self._dict_to_attr_on_obj(namespace, value)
                setattr(self, attr_name, namespace)
            else:
                setattr(self, attr_name, value)

    def _dict_to_attr_on_obj(self, obj: object, data: dict[str, Any]) -> None:
        for key, value in data.items():
            attr_name = key.upper()
            if isinstance(value, dict):
                namespace = type('ConfigNamespace', (), {})()
                self._dict_to_attr_on_obj(namespace, value)
                setattr(obj, attr_name, namespace)
            else:
                setattr(obj, attr_name, value)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.lower().split('.')
        value = self._config_data

        try:
            for k in keys:
                value = value[k]
            return value if value is not None else default
        except (KeyError, TypeError):
            return default


cfg = Configuration()
