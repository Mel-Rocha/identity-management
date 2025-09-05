from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from apps.users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    # api request can create only staff and common users - to create admin need to use django admin
    # in this implemantation username always will be email
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'username',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'write_only': True, 'required': True},
        }

    def create(self, validated_data):

        # Extrai a senha e valida força dela
        password = validated_data.pop('password')
        user = User(**validated_data)

        error = user.check_password_strength(password=password)
        if error:
            raise serializers.ValidationError({'password': error})

        user.set_password(password)  # salva senha de forma criptografada
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_superuser',
            'is_staff']
        read_only_fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_superuser',
            'is_staff']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'language',
            'timezone',
            'currency',
            'country',
            'organization',
            'address',
            'state',
            'zip_code',
            'phone_number',
        ]

    def validate_email(self, value):
        user_id = self.context.get('id')
        if User.objects.exclude(id=user_id).filter(email=value).exists():
            raise serializers.ValidationError("Usuário com este email já existe.")
        return value

    def validate(self, attrs):
        # Recupera o usuário alvo pelo id passado no contexto
        id = self.context.get('id')
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'detail': 'User not found'})

        # Garante que o usuário está ativo
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'This user is not activated'})

        # Adiciona o usuário ao contexto validado para ser usado na view
        attrs['user'] = user
        return attrs


class UserInactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Recupera o usuário alvo do contexto
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError({'detail': ['User not found']})

        if not user.is_active:
            raise serializers.ValidationError({'detail': ['User already inactivated']})

        attrs['user'] = user
        return attrs


class UserActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Recupera o id do contexto
        id = self.context.get('id')
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'detail': ['User not found']})

        if user.is_active:
            raise serializers.ValidationError(
                {'detail': ['User already Activated']})

        # Adiciona o usuário validado aos atributos
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['id', 'password', 'last_login', 'is_active', 'date_joined']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Token de refresh a ser invalidado.")