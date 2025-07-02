import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.permissions import IsStaffOrAdmin
from apps.users.serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserInactivateSerializer,
    UserActivateSerializer
)
from apps.users.models import User
from apps.users.tasks import task_send_password_reset_email


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
    View for user login.
    :permission_classes: Allow any user (unauthenticated) to access this view.
    :param email: User's email (required).
    :param password: User's password (required).
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
    View for user registration.
    :permission_classes: Allow any user (unauthenticated) to access this view.
    :param email: User's email (required).
    :param password: User's password (required).
    :param first_name: User's first name (optional).
    :param last_name: User's last name (optional).
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
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def put(self, request, id, *args, **kwargs):
        serializer = UserUpdateSerializer(
            data=request.data,
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Atualiza os campos recebidos
            for field, value in serializer.validated_data.items():
                if field != 'user':
                    setattr(user, field, value)
            user.username = user.email  # mantling the user creation username logic
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InactivateUser(APIView):
    """
    View for inactivating a user.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    """
    @staticmethod
    def delete(request, id, *args, **kwargs):
        serializer = UserInactivateSerializer(
            data={},
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = False
            user.save()
            return Response(
                {'message': 'Usuário inativado!'}, status=status.HTTP_204_NO_CONTENT)

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
                {'message': 'Usuário ativado!'}, status=status.HTTP_200_OK)

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
            tb = traceback.format_exc()  # Captura o traceback completo
            return Response(
                {
                    "error": f"Erro interno: {e}",
                    "traceback": tb  # Inclui o traceback na resposta (opcional)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Caso o email esteja registrado, as instruções foram enviadas."},
            status=status.HTTP_200_OK,
        )
