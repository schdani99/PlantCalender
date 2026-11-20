from django.shortcuts import render

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Plant
from .permissions import IsOwnerOrModerator
from .serializers import PlantSerializer


class PlantViewSet(viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user

        if user.role in ("moderator", "admin"):
            qs = Plant.objects.all()
        else:
            qs = Plant.objects.filter(
                Q(owner=user)
                | Q(visibility=Plant.Visibility.PUBLIC, owner__is_profile_public=True)
            )

        owner = self.request.query_params.get("owner")
        if owner:
            qs = qs.filter(owner__username=owner)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)