from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.filters import TitleFilter
from api.v1.permissions import (IsAdmin, IsAdminModeratorAuthorOrReadOnly,
                                IsAdminOrReadOnly, OwnerOnly)
from api.v1.serializers import (CategorySerializer, CommentSerializer,
                                GenreSerializer, ReviewSerializer,
                                SignUpSerializer, TitleSerializerGet,
                                TitleSerializerPost, TokenSerializer,
                                UserSerializer)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'name',
    )


class CategoryViewSet(BaseViewSet):
    """
    Получение списка категорий - доступно всем без токена.
    Создание категории, удаление категории - только администратору.
    """

    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class GenreViewSet(BaseViewSet):
    """
    Получение списка жанров - доступно всем без токена.
    Создание и удаление жанра - только администратору.
    Удаление происходит по slug.
    """

    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class TitleViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                   BaseViewSet):
    """
    Получение списка произведений - доступно всем без токена.
    Фильтрация по slug, году, названию, году.
    Создание, частичное изменение, удаление - только администратору.
    Нельзя добавлять произведения, которые еще не вышли.
    Получение объекта по titles_id - доступно всем без токена.
    """

    queryset = (
        Title.objects.prefetch_related(
            'genre',
        ).select_related(
            'category',
        ).order_by(
            'id',
        )
    )
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = TitleFilter
    permission_classes = (
        IsAdminOrReadOnly,
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializerGet
        return TitleSerializerPost


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение списка review, отдельного элемента."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                'title': self.kwargs['title_id'],
                'method': self.request.method,
            }
        )
        return context

    def get_queryset(self):
        return Review.objects.select_related(
            'author',
            'title',
        ).filter(
            title=self.kwargs.get('title_id'),
        ).order_by(
            'pub_date',
        )

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'),
        )
        serializer.save(
            author=self.request.user,
            title=title,
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Получение списка comment, отдельного элемента."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_queryset(self):
        return Comment.objects.select_related(
            'author',
            'review',
        ).filter(
            review=self.kwargs.get('review_id'),
        ).order_by(
            'pub_date',
        )

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
        )
        serializer.save(
            author=self.request.user,
            review=review,
        )


class APISignUp(APIView):
    """Регистрирует пользователя и отправляет код подтверждения на email."""

    def post(self, request):
        serializer = SignUpSerializer(
            data=request.data,
        )
        username = serializer.initial_data.get('username')
        email = serializer.initial_data.get('email')
        if not User.objects.filter(
            username=username,
            email=email,
        ).exists():
            serializer.is_valid(raise_exception=True)
            serializer.save()
        user = User.objects.get(
            username=username,
            email=email,
        )
        serializer = SignUpSerializer(
            user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
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
        return Response(
            serializer.validated_data,
            status=HTTP_200_OK,
        )


class APIToken(APIView):
    """Вернет JWT токен."""

    def post(self, request):
        serializer = TokenSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data.get('username'),
        )
        if default_token_generator.check_token(
                user,
                serializer.validated_data.get('confirmation_code'),
        ):
            token = {
                'token': f'{AccessToken.for_user(user)}'
            }
            return Response(
                token,
                status=HTTP_200_OK,
            )
        return Response(
            'Предоставленный код подтверждения неверен.',
            status=HTTP_400_BAD_REQUEST,
        )


class UsersViewSet(ModelViewSet):
    """Вернет/обновит информацию о пользователях. Создаст/удалит юзера."""

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (
        IsAdmin,
    )
    lookup_field = 'username'
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'username',
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    @action(
        methods=[
            'get',
            'patch',
        ],
        permission_classes=(
            OwnerOnly,
        ),
        url_path='me',
        detail=False,
    )
    def me_path(self, request):
        user = get_object_or_404(
            User,
            username=request.user,
        )
        if request.method == 'GET':
            serializer = UserSerializer(
                user,
            )
            return Response(
                serializer.data,
            )
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                role=request.user.role,
            )
            return Response(
                serializer.data,
                status=HTTP_200_OK,
            )