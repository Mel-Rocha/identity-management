import uuid
from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def userActive():
    return get_user_model().objects.create_user(
        email='testuser1',
        username='testuser1',
        password='password123',
        is_active=True
    )


@pytest.fixture
def userInactive():
    return get_user_model().objects.create_user(
        email='testuser2',
        username='testuser2',
        password='password123',
        is_active=False
    )


@pytest.mark.django_db
def test_inactivate_user(userActive):
    client = APIClient()
    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    url = '/users/user-inactivate-service/'

    # Agora enviamos o ID no body
    response = client.delete(
        url,
        data={'id': str(userActive.id)},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data == {'message': 'User successfully inactivated!'}

    userActive.refresh_from_db()
    assert not userActive.is_active
