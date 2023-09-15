from django.core.management.base import BaseCommand
from twentyfiveacres.models import Location

class Command(BaseCommand):
    help = 'Populate the Location model with 5 entries'

    def handle(self, *args, **kwargs):
        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            Location.objects.create(
                street_address=f'Street Address {i}',
                city=f'City {i}',
                state=f'State {i}',
                zip_code=f'ZIP {i}',
                country=f'Country {i}'
            )

        self.stdout.write(self.style.SUCCESS('Location model populated successfully'))
