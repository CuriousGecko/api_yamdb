from rest_framework.serializers import ModelSerializer

from users.models import CustomUser


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )
