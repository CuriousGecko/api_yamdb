from django.urls import include, path
from rest_framework import routers

from api.views import (APISignUp, APIToken, CategoryViewSet, GenreViewSet,
                       TitleViewSet, ReviewViewSet, CommentViewSet)

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genre', GenreViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

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
