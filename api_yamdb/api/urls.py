from api.views import TitleViewSet, CategoryViewSet, GenreViewSet
from django.urls import include, path
from rest_framework import routers
from django.urls import path, include

from api.views import APISignUp, APIToken

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genre', GenreViewSet)

auth_urls = [
    path(
        'signup/', APISignUp.as_view(), name='signup',
    ),
    path(
        'token/', APIToken.as_view(), name='token'
    )

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urls)),
]



