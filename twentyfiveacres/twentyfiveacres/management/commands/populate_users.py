'''
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    user_type = models.CharField(max_length=20, choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")])
    aadhar_number = models.CharField(max_length=20)
    document_hash = models.CharField(max_length=64)

'''

from django.core.management.base import BaseCommand
from twentyfiveacres.models import User

class Command(BaseCommand):
    help = 'Populate the User model with some buyers and sellers'

    def handle(self, *args, **kwargs):
        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            User.objects.create(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password',  # You should hash the password in a real application
                first_name=f'First{i}',
                last_name=f'Last{i}',
                phone_number=f'123-456-78{i}',
                # I want to create 5 buyers and 5 sellers
                user_type='buyer' if i % 2 == 1 else 'seller',  # Change user type as needed
                aadhar_number=f'123456789{i}',
                document_hash=f'123456789{i}'
            )

        self.stdout.write(self.style.SUCCESS('User model populated successfully'))
