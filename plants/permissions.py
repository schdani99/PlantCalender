from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrModerator(BasePermission):
    """Objektumszintű: a tulajdonos, moderator vagy admin módosíthat/törölhet."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ("moderator", "admin"):
            return True
        return obj.owner_id == user.id