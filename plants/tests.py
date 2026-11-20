from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Plant
from .models import Comment
from django.core.exceptions import ValidationError

User = get_user_model()


from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Comment, Plant

from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


from rest_framework import status
from rest_framework.test import APIClient


class PlantApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dani", password="titok123")
        self.other = User.objects.create_user(username="geza", password="titok123")

    def test_list_requires_authentication(self):
        response = self.client.get("/api/plants/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_returns_tokens(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "dani", "password": "titok123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_sees_only_own_plants(self):
        Plant.objects.create(owner=self.user, name="Monstera")
        Plant.objects.create(owner=self.other, name="Fikusz")
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/plants/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data["results"]] \
            if "results" in response.data else [p["name"] for p in response.data]
        self.assertEqual(names, ["Monstera"])

    def test_create_sets_owner_from_request_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/plants/", {"name": "Kaktusz"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plant.objects.get(name="Kaktusz").owner, self.user)

    def test_cannot_access_other_users_plant(self):
        plant = Plant.objects.create(owner=self.other, name="Fikusz")
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/plants/{plant.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        
        
