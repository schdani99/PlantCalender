from django.shortcuts import render

from rest_framework import viewsets

from .models import Plant
from .permissions import IsOwnerOrModerator
from .serializers import PlantSerializer
from rest_framework.permissions import IsAuthenticated

class PlantViewSet(viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        # 2. szelet: egyelőre csak a saját növények. A public/private
        # logika a 3. szeletben jön.
        return Plant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
