from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Admin").exists()


class IsNormalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Normal User").exists()
