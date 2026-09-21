from rest_framework import permissions


class IsLandlordOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.groups.filter(name='Landlords').exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsListingOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Для безопасных методов 
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для создания/изменения/удаления — только аутентифицированным
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # obj — это ListingPhoto
        return obj.listing.owner == request.user



