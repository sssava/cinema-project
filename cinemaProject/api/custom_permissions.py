from rest_framework import permissions


class IsOwnerOrAdminOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

    def has_permission(self, request, view):
        return True


class IsStaffOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff

    def has_permission(self, request, view):
        return request.user.is_staff
