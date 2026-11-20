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

        
        
