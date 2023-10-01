from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import (IsAdmin, IsAuthorOrReadOnly, OwnerOnly,
                             IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             ForAdminUsersSerializer, GenreSerializer,
                             NotAdminUsersSerializer, ReviewSerializer,
                             SignUpSerializer, TitleSerializer,
                             TokenSerializer)
from api_yamdb.settings import PRODUCT_EMAIL
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'name',
    )


class CategoryViewSet(BaseViewSet):
    """Получение списка категорий - доступно всем без токена.
    Создание категории, удаление категории - только администратору.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class GenreViewSet(BaseViewSet):
    """Получение списка жанров - доступно всем без токена.
    Создание и удаление жанра - только администратору.
    Удаление происходит по slug.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # Это поле (оно же добавлено в serializers) позволяет сделать маршруты
    # автоматически по slug, по дефолту установлены ID. Т.е.
    # раньше, чтобы получить объект - http://127.0.0.1:8000/api/v1/genre/1/
    # теперь http://127.0.0.1:8000/api/v1/genre/skazka/
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )


class TitleViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                   BaseViewSet):
    """Получение списка произведений - доступно всем без токена.
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
        )
    )
    serializer_class = TitleSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )
    permission_classes = (
        IsAdminOrReadOnly,
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )


class ReviewViewSet(viewsets.ModelViewSet):
    """Просмотр обзоров-все пользователи.
    Добавление, изменение, удаление - только авторизованные.
    Изменяет отзыв только его автор.
    """
    serializer_class = ReviewSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly,
    #     IsAuthorOrReadOnly,
    # )

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        review_queryset = Review.objects.select_related(
            'title').filter(pk=title.id).all()
        return review_queryset

    # def create(self, validated_data):
    #     return Review(**validated_data)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """Просмотр комментариев-все пользователи.
    Добавление, изменение, удаление - только авторизованные.
    Изменяет комментарий только его автор.
    """

    # queryset = Comment.objects.all()
    # serializer_class = CommentSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly,
    #     IsAuthorOrReadOnly,
    # )

    # def get_review(self):
    #     review_id = self.kwargs.get('review_id')
    #     return get_object_or_404(Review, pk=review_id)

    # def get_queryset(self):
    #     review = self.get_review()
    #     comment_queryset = Comment.objects.select_related(
    #         'review').filter(review=review).all()
    #     return comment_queryset

    # def perform_create(self, serializer):
    #     review = self.get_review()
    #     serializer.save(author=self.request.user, review=review)


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
            username=request.data.get('username')
        )
        if (
            serializer.validated_data.get('confirmation_code')
            == str(user.confirmation_code)
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

    queryset = User.objects.all()
    serializer_class = ForAdminUsersSerializer
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
            serializer = NotAdminUsersSerializer(
                user,
            )
            return Response(
                serializer.data,
            )
        if request.method == 'PATCH':
            serializer = NotAdminUsersSerializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=HTTP_200_OK,
            )
