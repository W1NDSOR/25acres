from django.core.management.base import BaseCommand
from twentyfiveacres.models import User

class Command(BaseCommand):
    help = 'Populate the User model with 5 entries'

    def handle(self, *args, **kwargs):
        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            User.objects.create(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password',  # You should hash the password in a real application
                first_name=f'First{i}',
                last_name=f'Last{i}',
                phone_number=f'123-456-78{i}',
                user_type='buyer'  # Change user type as needed
            )

        self.stdout.write(self.style.SUCCESS('User model populated successfully'))
