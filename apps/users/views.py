import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.logs import logger
from apps.users.permissions import IsStaffOrAdmin
from apps.users.serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserInactivateSerializer,
    UserActivateSerializer, LogoutSerializer, UserSerializer
)
from apps.users.models import User
from apps.users.tasks import task_send_password_reset_email
from apps.users.utils import get_target_user
from apps.users.choices import LanguageChoices, CountryChoices, CurrencyChoices, TimezoneChoices


class ListUsers(ListAPIView):
    """
    View for listing all users.
    :permission_classes: Only authenticated staff or admin users can access this view.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    serializer_class = UserRetrieveSerializer
    pagination_class = PageNumberPagination
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if not response.data['results']:
            response.data['message'] = 'No users found'
        return response

class RetrieveUser(APIView):
    """
    View for retrieving a specific user by ID.
    """
    def get(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            serializer = UserRetrieveSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    View para login de usuário.

    :permission_classes: Permite qualquer usuário (não autenticado) acessar esta view.

    :param email: E-mail do usuário (obrigatório).
    :param password: Senha do usuário (obrigatória).
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid credentials'},
                                status=status.HTTP_401_UNAUTHORIZED)
            try:
                if not user.is_active:
                    return Response({'message': 'User is inactive'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid credentials'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(password):
                return Response({'message': 'Invalid credentials'},
                                status=status.HTTP_401_UNAUTHORIZED)

            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    """
    Registro de usuários.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUser(APIView):
    """
    View for updating user information.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    :param email: User's email (optional).
    :param first_name: User's first name (optional).
    :param last_name: User's last name (optional).
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def put(self, request, *args, **kwargs):
        id_from_body = request.data.get('id')  # id opcional vindo do body

        # ==============================================================
        # ATENÇÃO: risco de IDOR (Insecure Direct Object Reference) se
        # permitirmos que usuários comuns passem o 'id' de outro usuário.
        # Para mitigar, apenas superusers podem usar o id passado.
        # ==============================================================

        target_user = get_target_user(request.user, id=id_from_body)

        # Cria o serializer passando o usuário alvo como instance
        serializer = UserUpdateSerializer(
            instance=target_user,
            data=request.data,
            context={'id': target_user.id, 'request': request},
            partial=True
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InactivateUser(APIView):
    """
    View for inactivating a user.
    :permission_classes: Only authenticated staff or admin users can access this view.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserInactivateSerializer)
    def delete(self, request, *args, **kwargs):
        # Lê o id opcional do body
        id_from_body = request.data.get('id')

        # Determina o usuário alvo usando função utilitária
        target_user = get_target_user(request.user, id=id_from_body)

        # Cria o serializer para validação
        serializer = UserInactivateSerializer(
            data={},
            context={'user': target_user, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = False
            user.save()
            return Response(
                {'message': 'User successfully inactivated!'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUser(APIView):
    """
    View for activating a user.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    """
    @staticmethod
    def put(request, id, *args, **kwargs):
        serializer = UserActivateSerializer(
            data={},
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return Response(
                {'message': 'User sucessfully activated!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecoverPassword(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='E-mail do usuário'),
            },
            required=['email'],
        )
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "E-mail é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            new_password = user.reset_password()
            task_send_password_reset_email.delay(user.id, new_password)
        except User.DoesNotExist:
            # Silenciar esse erro evita exploração por enumeration
            pass
        except Exception as e:
            # Registra o erro com traceback completo, sem expor ao usuário
            logger.error("Erro ao tentar recuperar senha para %s: %s\n%s", email, e, traceback.format_exc())

            return Response(
                {"error": "Erro interno ao processar a solicitação."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Caso o email esteja registrado, as instruções foram enviadas."},
            status=status.HTTP_200_OK,
        )

class LogoutView(APIView):
    """
    - Objetivo:
        Invalidar o refresh token do usuário, realizando logout seguro.

    - Permissões:
        Usuários autenticados (todos os perfis de usuários).

    - Retorno:
        JSON (205 Reset Content ou 400 Bad Request)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={
            205: openapi.Response("Logout realizado com sucesso."),
            400: openapi.Response("Erro de validação ou token inválido."),
        },
    )

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token ausente."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # ← aqui é onde ele vai para a blacklist
            return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"detail": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    - Objetivo:
        Retornar os dados do usuário autenticado.

    - Permissões:
        Usuários autenticados (todos os perfis de usuários).

    - Retorno:
        JSON (200 OK)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChoicesListView(APIView):
    """
    Endpoint para listar opções de enums (choices).
    Query param: type=[language|country|currency|timezone]
    Default: language
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Tipo de choices: language, country, currency, timezone",
                type=openapi.TYPE_STRING,
                enum=['language', 'country', 'currency', 'timezone'],
                required=False,
                default='language'
            )
        ]
    )
    def get(self, request):
        choice_type = request.query_params.get('type', 'language').lower()
        choices_map = {
            'language': LanguageChoices,
            'country': CountryChoices,
            'currency': CurrencyChoices,
            'timezone': TimezoneChoices,
        }
        choices_class = choices_map.get(choice_type, LanguageChoices)
        data = [
            {'value': c.value, 'label': c.label}
            for c in choices_class
        ]
        return Response(data, status=status.HTTP_200_OK)