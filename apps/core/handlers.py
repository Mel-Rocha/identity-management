import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Chama o handler padrão do DRF
    response = exception_handler(exc, context)

    # Se DRF conseguiu lidar com a exceção (ex: APIException)
    if response is not None:
        data = response.data
        if "detail" in data:
            # Erro global (ex: PermissionDenied)
            message = data["detail"]
            code = getattr(exc, 'default_code', 'error')
        else:
            # Erro de campo (ex: validação de serializer)
            message = data
            code = getattr(exc, 'default_code', 'invalid')

        response.data = {
            "message": message,
            "code": code,
            "status": response.status_code,
        }
        return response

    # Lida com exceções que o DRF normalmente ignora (500, TypeError, etc)
    view = context.get('view', None)
    request = context.get('request', None)

    logger.error(
        "Erro interno não tratado",
        exc_info=exc,
        extra={
            "view": view.__class__.__name__ if view else None,
            "method": request.method if request else None,
            "path": request.path if request else None,
        }
    )

    return Response(
        {
            "message": "Erro interno do servidor",
            "code": "internal_server_error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
