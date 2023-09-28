from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from reviews.models import Category, Genre, Title
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters, viewsets, mixins
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from api.serializers import SignUpSerializer
from django_filters.rest_framework import DjangoFilterBackend


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(BaseViewSet):
    """Получение списка категорий - доступно всем без токена.
    Создание категории, удаление категории - только администратору.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    # permission_classes = (IsOwnerOrReadOnly, )


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



class TitleViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                   BaseViewSet):
    """Получение списка произведений - доступно всем без токена.
    Фильтрация по slug, году, названию, году.
    Создание, часчтичное изменение, удаление - только администратору. 
    Нельзя добавлять произведения, которые еще не вышли.
    Получение объекта по titles_id - доступно всем без токена.
    """
    queryset = Title.objects.prefetch_related('genre').select_related('category')
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year') 


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
