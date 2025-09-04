from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from apps.users.models import User


def get_target_user(request_user, id=None):
    """
    Retorna o usuário alvo para update/inactivate.

    - Superusers podem passar um `id` para editar outro usuário.
    - Usuários comuns sempre retornam a si mesmos.
    - Levanta ValidationError se o usuário alvo não existir.
    """
    if request_user.is_superuser and id:
        try:
            target_user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'Usuário não encontrado.'})
    else:
        target_user = request_user

    return target_user
