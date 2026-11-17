"""
Management command: create_superusers
Creates initial superuser accounts for production deployment.
Superusers automatically get is_staff=True, giving them full admin access in the LMS.
"""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


SUPERUSERS = [
    {
        "username": "admin",
        "password": "admin123",
        "email": "",
    },
]


class Command(BaseCommand):
    help = "Create default superuser accounts if they do not already exist."

    def handle(self, *args, **options):
        User = get_user_model()
        for data in SUPERUSERS:
            username = data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"Superuser '{username}' already exists – skipped.")
                continue
            User.objects.create_superuser(
                username=username,
                email=data.get("email", ""),
                password=data["password"],
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
