from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from api.serializers import (CategorySerializer, GenreSerializer,
                             SignUpSerializer, TitleSerializer)
from api_yamdb.settings import PRODUCT_EMAIL
from reviews.models import Category, Genre, Title

User = get_user_model()


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    # permission_classes = (IsOwnerOrReadOnly, )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class APISignUp(APIView):
    """Регистрирует пользователя и отправляет код подтверждения на email."""

    def post(self, request):
        serializer = SignUpSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            **serializer.validated_data,
        )
        email = serializer.validated_data.get('email')
        send_mail(
            subject='Запрошен код подтверждения для доступа к API YaMDb.',
            message=(
                f'Ваш код подтверждения: {user.confirmation_code}'
            ),
            from_email=PRODUCT_EMAIL,
            recipient_list=(
                email,
            ),
            fail_silently=False,
        )
        return Response(
            serializer.validated_data, status=HTTP_200_OK
        )


class APIToken(APIView):
    pass
