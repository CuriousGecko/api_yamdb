from .serializers import (
    CategorySerializer, GenreSerializer,
    TitleSerializer, ReviewSerializer, CommentSerializer
)
from reviews.models import Category, Genre, Title, Review, Comment
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import filters, viewsets, mixins
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from api.serializers import SignUpSerializer
from permissions import IsAuthorOrReadOnly


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    # permission_classes = (IsOwnerOrReadOnly, )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


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


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # pagination_class = PageNumberPagination
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ('name',)
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
