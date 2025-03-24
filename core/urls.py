from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (AccountViewSet,
                    DestinationViewSet,
                    AccountMemberViewSet,
                    LogViewSet,
                    RegisterView,
                    CustomAuthToken,
                    IncomingDataAPIView, WebhookTestView)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'account-members', AccountMemberViewSet)
router.register(r'logs', LogViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomAuthToken.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("server/incoming_data/", IncomingDataAPIView.as_view(), name="incoming_data"),
    path("webhook-test/", WebhookTestView.as_view(), name="webhook_test"),

]
