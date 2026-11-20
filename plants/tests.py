from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Plant

User = get_user_model()


class PlantModelTests(TestCase):
    def test_plant_is_private_by_default_and_has_owner(self):
        user = User.objects.create_user(username="dani", password="titok123")
        plant = Plant.objects.create(owner=user, name="Monstera")

        self.assertEqual(plant.owner, user)
        self.assertEqual(plant.visibility, Plant.Visibility.PRIVATE)
        self.assertIn(plant, user.plants.all())