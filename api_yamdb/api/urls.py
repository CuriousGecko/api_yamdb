from api.views import TitleViewSet, CategoryViewSet, GenreViewSet
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genre', GenreViewSet)

urlpatterns = [
    path('', include(router.urls)),
]