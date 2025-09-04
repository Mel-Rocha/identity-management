import random
import re
from string import ascii_letters, digits
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission

from apps.users.choices import LanguageChoices, TimezoneChoices, CurrencyChoices


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    last_login = models.DateTimeField(
        auto_now=True, verbose_name='Último Acesso')
    first_name = models.CharField(max_length=30, verbose_name='Nome')
    last_name = models.CharField(max_length=30, verbose_name='Sobrenome')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    # to be a django admin must be both is_staff and is_superuser
    # super access users - can do anything in this system except use django
    # admin
    is_superuser = models.BooleanField(
        default=False, verbose_name='Administrador')
    # medium access users - can update or delete  | if not super and not staff
    # is common_user
    is_staff = models.BooleanField(default=False, verbose_name='Equipe')

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Change related_name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='Grupos',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        # Change related_name to avoid conflict
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='Permissões de usuário',
    )

    language = models.CharField(
        max_length=5,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH,
    )
    timezone = models.CharField(
        max_length=20,
        choices=TimezoneChoices.choices,
        default=TimezoneChoices.UTC,
    )
    currency = models.CharField(
        max_length=5,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_user_access_level(self):
        if not self.is_superuser:
            if not self.is_staff:
                return "common_user"
            return "staff_user"
        return "super_user"

    @staticmethod
    def check_password_strength(password: str or False):
        if not password:
            return 'Senha inválida!'

        not_valid = False
        if len(password) < 8:
            not_valid = 'Senha deve conter pelo menos 8 caracteres!'
            return not_valid
        if not re.search("[a-z]", password):
            not_valid = 'Senha deve conter pelo menos uma letra minuscula!'
            return not_valid
        if not re.search("[A-Z]", password):
            not_valid = 'Senha deve conter pelo menos uma letra maiuscula!'
            return not_valid
        if not re.search("[0-9]", password):
            not_valid = 'Senha deve conter pelo menos um número!'
            return not_valid
        if not re.search("[_@!()&+$?*=%#;:-]", password):
            not_valid = ('Senha deve conter pelo menos uma dos seguintes '
                         'simbolos: _ @ ! ( ) & + $ ? * - = % # ; :')
            return not_valid
        if re.search("\\s", password):
            not_valid = 'Espaços vazios não são permitidos!'

        return not_valid

    def change_password(self, current_password: str, new_password):
        if self.check_password_strength(current_password):
            check_password = self.check_password_strength(new_password)
            if not check_password:
                self.set_password(new_password)
                self.save()
                return True, 'Senha alterada com sucesso! Faça login com sua nova senha!'
            return False, check_password
        return False, 'Senha atual inválida!'

    def reset_password(self) -> str:
        """Gera e define uma nova senha para o usuário."""
        new_password = self._generate_secure_password()
        self.set_password(new_password)
        self.save()
        return new_password

    @staticmethod
    def _generate_secure_password(length: int = 12) -> str:
        characters = list(ascii_letters + digits + "!@#$%&*()")
        random.shuffle(characters)
        return ''.join(random.choice(characters) for _ in range(length))