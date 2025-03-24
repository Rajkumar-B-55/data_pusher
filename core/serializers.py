from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group

from .models import Account, Destination, AccountMember, Log


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)
        Token.objects.create(user=user)
        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ["app_secret_token", "created_at", "updated_at"]


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class AccountMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    role = serializers.SlugRelatedField(slug_field="name", queryset=Group.objects.all())

    class Meta:
        model = AccountMember
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
