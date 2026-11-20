from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrModerator(BasePermission):
    """Objektumszintű: a tulajdonos, moderator vagy admin módosíthat/törölhet."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True  # a láthatóságot a get_queryset már eldöntötte
        user = request.user
        if user.role in ("moderator", "admin"):
            return True
        return obj.owner_id == user.id

    