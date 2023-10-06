from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_code(user, email):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Запрошен код подтверждения для доступа к API YaMDb.',
        message=(
            f'Ваш код подтверждения: {confirmation_code}'
        ),
        from_email=settings.PRODUCT_EMAIL,
        recipient_list=(
            email,
        ),
        fail_silently=False,
    )
