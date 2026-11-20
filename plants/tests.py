from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Comment, Plant

User = get_user_model()


class PlantModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dani", password="titok123")
        self.plant = Plant.objects.create(owner=self.user, name="Monstera")

    def test_plant_is_private_by_default(self):
        self.assertEqual(self.plant.visibility, Plant.Visibility.PRIVATE)

    def test_plant_belongs_to_owner(self):
        self.assertEqual(self.plant.owner, self.user)
        self.assertIn(self.plant, self.user.plants.all())


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dani", password="titok123")
        self.plant = Plant.objects.create(owner=self.user, name="Monstera")

    def test_comment_is_linked_to_plant_and_author(self):
        comment = Comment.objects.create(
            plant=self.plant, author=self.user, text="Szép levelek!"
        )
        self.assertEqual(comment.plant, self.plant)
        self.assertEqual(comment.author, self.user)
        self.assertIn(comment, self.plant.comments.all())

    def test_comment_text_cannot_be_blank(self):
        comment = Comment(plant=self.plant, author=self.user, text="")
        with self.assertRaises(ValidationError):
            comment.full_clean()


class PlantApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dani", password="titok123")
        self.other = User.objects.create_user(username="geza", password="titok123")

    def names(self, response):
        data = response.data["results"] if "results" in response.data else response.data
        return [p["name"] for p in data]

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
        self.assertEqual(self.names(response), ["Monstera"])

    def test_create_sets_owner_from_request_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/plants/", {"name": "Kaktusz"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plant.objects.get(name="Kaktusz").owner, self.user)

    def test_cannot_access_other_users_private_plant(self):
        plant = Plant.objects.create(owner=self.other, name="Fikusz")
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/plants/{plant.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_sees_public_plant_of_public_profile(self):
        self.other.is_profile_public = True
        self.other.save()
        Plant.objects.create(
            owner=self.other, name="Fikusz", visibility=Plant.Visibility.PUBLIC
        )
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/plants/?owner=geza")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.names(response), ["Fikusz"])

    def test_private_plant_of_other_user_is_hidden(self):
        self.other.is_profile_public = True
        self.other.save()
        Plant.objects.create(owner=self.other, name="Titkos")  # alapból private
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/plants/?owner=geza")

        self.assertEqual(self.names(response), [])

    def test_cannot_edit_other_users_public_plant(self):
        self.other.is_profile_public = True
        self.other.save()
        plant = Plant.objects.create(
            owner=self.other, name="Fikusz", visibility=Plant.Visibility.PUBLIC
        )
        self.client.force_authenticate(self.user)

        response = self.client.patch(f"/api/plants/{plant.id}/", {"name": "Hacked"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)