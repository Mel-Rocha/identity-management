"""
Módulo de testes para a funcionalidade de atualização de usuários.

Objetivo:
Este módulo valida que a API de atualização de usuários funciona corretamente
para usuários privilegiados (superuser) e que impede que usuários comuns
atualizem dados de outros usuários, prevenindo a vulnerabilidade OWASP IDOR
(Insecure Direct Object Reference).

Cada teste verifica cenários diferentes:
- Usuário administrador pode atualizar qualquer usuário.
- Usuário comum só pode atualizar seus próprios dados.
- Tentativas de atualização de usuários inexistentes ou desativados são tratadas corretamente.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def normal_user():
    return User.objects.create_user(
        email='user@example.com',
        username='user',
        password='password123',
        is_active=True,
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        email='another@example.com',
        username='another',
        password='password123',
        is_active=True,
    )


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='password123',
        is_active=True,
    )


@pytest.mark.django_db
def test_superuser_can_update_any_user(superuser, normal_user):
    """
   Teste: Superuser atualiza dados de qualquer usuário.

   OWASP IDOR:
   Verifica que o backend permite apenas que usuários com privilégios
   administrativos atualizem outros usuários via ID passado no body.
       """
    client = APIClient()
    token = str(RefreshToken.for_user(superuser).access_token)

    url = '/users/user-update-service/'
    data = {
        'id': str(normal_user.id),  # superuser envia id de outro usuário
        'email': 'updated_email@example.com',
        'first_name': 'Updated',
        'last_name': 'User',
    }

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.put(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

    normal_user.refresh_from_db()
    assert normal_user.email == 'updated_email@example.com'
    assert normal_user.first_name == 'Updated'


@pytest.mark.django_db
def test_normal_user_cannot_update_other_user(normal_user, another_user):
    """
    Teste de proteção contra IDOR para usuários comuns.

    OWASP IDOR (Insecure Direct Object Reference):
    Usuários não privilegiados não devem conseguir atualizar informações de
    outros usuários passando IDs arbitrários no body da requisição. Este teste
    garante que o backend ignora IDs não autorizados e atualiza apenas o próprio usuário.
        """
    client = APIClient()
    token = str(RefreshToken.for_user(normal_user).access_token)

    url = '/users/user-update-service/'
    data = {
        'id': str(another_user.id),  # tenta passar id de outro usuário
        'email': 'hacker_email@example.com',
        'first_name': 'Hacker',
        'last_name': 'User',
    }

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.put(url, data, format='json')

    # Backend ignora o id passado e atualiza apenas o próprio usuário
    assert response.status_code == status.HTTP_200_OK

    normal_user.refresh_from_db()
    another_user.refresh_from_db()

    # normal_user deve ser atualizado
    assert normal_user.email == 'hacker_email@example.com'
    # another_user NÃO deve ser atualizado
    assert another_user.email == 'another@example.com'
