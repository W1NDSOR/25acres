from django.core.management.base import BaseCommand
from twentyfiveacres.models import Image, Property, User

class Command(BaseCommand):
    help = 'Populate the Image model with 5 entries'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        users = User.objects.all()

        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            property = properties[i - 1]  # Get the property with the same index
            user = users[i - 1] if i % 2 == 0 else None  # Assign user every 2 iterations

            Image.objects.create(
                property=property,
                user=user,
                image_url=f'https://example.com/images/image{i}.jpg',  # Change URL as needed
            )

        self.stdout.write(self.style.SUCCESS('Image model populated successfully'))
