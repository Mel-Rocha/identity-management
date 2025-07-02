from celery import shared_task
from django.core.mail import send_mail

from apps.users.models import User
from apps.core.logs import logger
from config.settings import DEFAULT_FROM_EMAIL


@shared_task(
    name="task_send_password_reset_email",
    queue="queue_send_password_reset_email",
)
def task_send_password_reset_email(user_id, new_password):
    logger.info("Iniciando envio de nova senha por e-mail")

    try:
        user = User.objects.get(pk=user_id)

        subject = 'Sua nova senha'
        plain_message = f'Sua nova senha de acesso é: {new_password}'

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info("E-mail de nova senha enviado para: " + user.email)

    except Exception as e:
        logger.error("[task_send_password_reset_email] Erro ao enviar e-mail: " + str(e))