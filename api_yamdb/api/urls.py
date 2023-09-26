from django.urls import path, include

from api.views import APISignUp, APIToken

auth_urls = [
    path(
        'signup/', APISignUp.as_view(), name='signup',
    ),
    path(
        'token/', APIToken.as_view(), name='token'
    )
]

urlpatterns = [
    # path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_urls)),
]