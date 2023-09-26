from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from api.serializers import SignUpSerializer

User = get_user_model()


class APISignUp(APIView):
    """Регистрирует пользователя и отправляет код подтверждения на email."""

    def post(self, request):
        serializer = SignUpSerializer(
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            User.objects.create_user(
                **request.data
            )
        user = User.objects.get(username=request.data.get('username'))
        send_mail(
            subject='Запрошен код подтверждения для доступа к API YaMDb.',
            message=(
                f'Ваш confirmation_code: {user.confirmation_code}'
            ),
            from_email='Cyber@Pochta.ai',
            recipient_list=[request.data.get('email')],
            fail_silently=False,
        )
        return Response(
            user.confirmation_code, status=HTTP_200_OK
        )


class APIToken(APIView):
    pass
