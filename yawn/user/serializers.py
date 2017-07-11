from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    api_token = serializers.CharField(source='auth_token.key', read_only=True)
    refresh_token = serializers.BooleanField(write_only=True, default=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'api_token', 'email',
                  'refresh_token', 'id', 'password', 'is_staff')

    def create(self, validated_data):
        validated_data.pop('refresh_token', None)
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # support refreshing the token:
        if validated_data.pop('refresh_token', False):
            if hasattr(instance, 'auth_token'):
                instance.auth_token.delete()
            instance.auth_token = Token.objects.create(user=instance)
        # and setting the password, which causes an unhandled logout...
        if validated_data.get('password'):
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
