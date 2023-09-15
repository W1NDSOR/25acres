from django.core.management.base import BaseCommand
from twentyfiveacres.models import Property, Location

class Command(BaseCommand):
    help = 'Populate the Property model with 5 entries'

    def handle(self, *args, **kwargs):
        location = Location.objects.first()  # You can choose an existing location or create one

        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            Property.objects.create(
                title=f'Property {i}',
                description=f'Description for Property {i}',
                price=100000 + i * 20000,
                property_type='House',
                bedrooms=3,
                bathrooms=2,
                area=150.0 + i * 10,
                status='for_sale',
                availability_date='2023-09-15',
                location=location
            )

        self.stdout.write(self.style.SUCCESS('Property model populated successfully'))
