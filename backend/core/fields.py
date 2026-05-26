"""
Custom encrypted field using cryptography.fernet.
Replacement for django-fernet-fields which is incompatible with Django 6.
"""
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, MultiFernet


def _get_fernet():
    keys = settings.FERNET_KEYS
    if isinstance(keys[0], str):
        keys = [k.encode() for k in keys]
    return MultiFernet([Fernet(k) for k in keys])


class EncryptedTextField(models.TextField):
    """TextField that encrypts values at rest using Fernet symmetric encryption."""

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            f = _get_fernet()
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value  # already plaintext (migration scenario)

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        if not value:
            return value
        f = _get_fernet()
        return f.encrypt(value.encode()).decode()
