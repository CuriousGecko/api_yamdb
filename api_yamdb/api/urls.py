from django.urls import include, path
from rest_framework import routers

from api.views import (APISignUp, APIToken, CategoryViewSet,
                       GenreViewSet, TitleViewSet, UsersViewSet)

router = routers.DefaultRouter()
router.register('titles', TitleViewSet, basename='titles',)
router.register('categories', CategoryViewSet, basename='categories',)
router.register('genre', GenreViewSet, basename='genre',)
router.register('users', UsersViewSet, basename='users',)

auth_urls = [
    path(
        'signup/', APISignUp.as_view(), name='signup',
    ),
    path(
        'token/', APIToken.as_view(), name='token',
    ),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urls)),
]



