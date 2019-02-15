from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework.serializers import (Serializer, ModelSerializer, CharField,
                                        ValidationError)

class UserSerializer(ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = 'email', 'password', 'name'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """Create a new user with excrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

class AuthTokenSerializer(Serializer):
    """Serializer for the user authentication object."""
    email = CharField()
    password = CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            message = _('Wrong credentials')
            raise ValidationError(message, code='authencation')
        
        attrs['user'] = user
        return attrs
