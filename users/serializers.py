from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_admin', 'created_at', 'password']
        read_only_fields = ['id', 'created_at']

    def save(self, validated_data):
        # if validated_data['is_admin']:
        #     return self.create_admin(validated_data)
        # return self.create_user(validated_data)
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_admin=validated_data['is_admin']
        )

        user.set_password(validated_data['password'])

        user.save()

        return user
        
    

class TokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(TokenPairSerializer, cls).get_token(user)
        token['role'] = 'user'
        if user.is_admin:
            token['role'] = 'admin'
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email
        data['role'] = 'user'
        if self.user.is_admin:
            data['role'] = 'admin'

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data