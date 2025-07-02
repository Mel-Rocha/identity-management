from rest_framework.permissions import BasePermission


# class IsAdminUser(BasePermission):
#     """
#     Permite acesso aos utilizadores Administradores
#     """
#
#     def has_permission(self, request, view):
#         return request.user and request.user.is_admin


class IsStaffOrAdmin(BasePermission):
    """
    Permissão personalizada para permitir que somente usuários da equipe
    ou administradores acessem a visualização.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff or request.user.is_superuser
