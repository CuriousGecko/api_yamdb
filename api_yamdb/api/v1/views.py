from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.filters import TitleFilter
from api.v1.permissions import (IsAdmin, IsAdminModeratorAuthorOrReadOnly,
                                IsAdminOrReadOnly, OwnerOnly)
from api.v1.serializers import (CategorySerializer, CommentSerializer,
                                GenreSerializer, ReviewSerializer,
                                SignUpSerializer, TitleCreateSerializer,
                                TitleGetSerializer, TokenSerializer,
                                UserSerializer)
from api.v1.utils import send_confirmation_code
from api.v1.viewsets import (ListCreateDestroyViewSet,
                             ListCreateRetrievePatchDestroyViewSet)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Обрабатывает запросы, связанные с категориями.

    Получение списка категорий - доступно всем без токена.
    Создание категории, удаление категории - только администратору.
    """

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Обрабатывает запросы, связанные с категориями.

    Получение списка жанров - доступно всем без токена.
    Создание и удаление жанра - только администратору.
    Удаление происходит по slug.
    """

    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class TitleViewSet(ListCreateRetrievePatchDestroyViewSet):
    """
    Обрабатывает запросы, связанные с записями.

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
            'name',
        ).annotate(
            rating=Avg('reviews__score'),
        )
    )
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = TitleFilter
    permission_classes = (
        IsAdminOrReadOnly,
    )

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleGetSerializer
        return TitleCreateSerializer


class ReviewViewSet(ListCreateRetrievePatchDestroyViewSet):
    """Получает список review, отдельный элемент."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
    )

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
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title,
                pk=self.kwargs.get('title_id'),
            )
        )


class CommentViewSet(ListCreateRetrievePatchDestroyViewSet):
    """Получение списка comment, отдельного элемента."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
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
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review,
                pk=self.kwargs.get('review_id'),
            )
        )


class APISignUp(APIView):
    """Регистрирует пользователя и отправляет код подтверждения на email."""

    def post(self, request):
        serializer = SignUpSerializer(
            data=request.data,
        )
        if not serializer.is_valid():
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            if User.objects.filter(
                    username=username,
                    email=email,
            ).exists():
                send_confirmation_code(
                    user=User.objects.get(
                        username=username,
                        email=email,
                    ),
                    email=email,
                )
                return Response(
                    serializer.data,
                    status=HTTP_200_OK,
                )
            raise ValidationError(serializer.errors)
        serializer.save()
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        send_confirmation_code(
            user=User.objects.get(
                username=username,
                email=email,
            ),
            email=email,
        )
        return Response(
            serializer.validated_data,
            status=HTTP_200_OK,
        )


class APIToken(APIView):
    """Возвращает JWT токен."""

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


class UsersViewSet(ListCreateRetrievePatchDestroyViewSet):
    """
    Обрабатывает запросы, связанные с пользователями.

    Возвращает/обновляет информацию о пользователях.
    Создает/удаляет пользователя.
    """

    queryset = User.objects.all()
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

    @action(
        methods=[
            'get'
        ],
        permission_classes=(
                OwnerOnly,
        ),
        url_path='me',
        detail=False,
    )
    def me_path(self, request):
        serializer = UserSerializer(
            get_object_or_404(
                User,
                username=request.user,
            )
        )
        return Response(
            serializer.data,
        )

    @me_path.mapping.patch
    def me_path_patch(self, request):
        serializer = UserSerializer(
            get_object_or_404(
                User,
                username=request.user,
            ),
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
