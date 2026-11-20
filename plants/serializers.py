from rest_framework import serializers

from .models import Plant


class PlantSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Plant
        fields = [
            "id", "owner", "name", "species", "photo",
            "visibility", "allow_comments", "last_watered_at", "created_at",
        ]
        read_only_fields = ["id", "owner", "created_at"]