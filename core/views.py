import json
import uuid

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, permissions, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Destination, AccountMember, Log
from .permissions import IsAdmin
from .serializers import (AccountSerializer,
                          DestinationSerializer,
                          AccountMemberSerializer,
                          LogSerializer,
                          UserSerializer)
from .utils import create_log
from .tasks import send_data_to_destination


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        return Response({"token": token.key, "user_id": token.user.id, "username": token.user.username})


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().prefetch_related("destinations")
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def list(self, request, *args, **kwargs):
        cache_key = "accounts_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # 5 minutes
        return response


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AccountMemberViewSet(viewsets.ModelViewSet):
    queryset = AccountMember.objects.all()
    serializer_class = AccountMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all().order_by("-received_timestamp")
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated]


class IncomingDataAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key="header:CL-X-TOKEN", rate="5/s", method="POST", block=True))
    def post(self, request):
        app_secret_token = request.headers.get("CL-X-TOKEN")
        event_id = request.headers.get("CL-X-EVENT-ID", str(uuid.uuid4()))

        print("app_secret_token", app_secret_token)
        print("event_id", event_id)

        if not app_secret_token:
            return Response({"success": False, "message": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            account = Account.objects.get(app_secret_token=app_secret_token)
        except Account.DoesNotExist:
            return Response({"success": False, "message": "Invalid Token"}, status=status.HTTP_403_FORBIDDEN)

        if not isinstance(request.data, dict):
            return Response({"success": False, "message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
        create_log(event_id, account, request.data)

        for destination in account.destinations.all():
            print(f"🚀 Sending Data to Destination ID: {destination.id}, URL: {destination.url}")
            send_data_to_destination.delay(str(destination.id), str(event_id),
                                           json.dumps(request.data))  # Convert to string

        return Response({"success": True, "message": "Data Received"}, status=status.HTTP_202_ACCEPTED)


class WebhookTestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("Webhook Received:", request.data)
        return Response({"success": True, "message": "Webhook received"}, status=status.HTTP_200_OK)
