from django.contrib import admin

from .models import Comment, Plant, Reminder


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "visibility", "allow_comments", "created_at")
    list_filter = ("visibility", "allow_comments")
    search_fields = ("name", "species", "owner__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("plant", "author", "created_at")


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("title", "plant", "due_date", "is_done")
    list_filter = ("is_done",)