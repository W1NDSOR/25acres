# Location Model

'''
    class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

'''

from django.core.management.base import BaseCommand
from location.models import Location

class Command(BaseCommand):
    help = 'Populate the **table** with sample data'

    def handle(self, *args, **kwargs):
        print('Populating Location model...')

        for i in range(1, 6): 
            Location.objects.create(
                street_address=f'Street Address {i}',
                city=f'City {i}',
                state=f'State {i}',
                zip_code=f'ZIP {i}',
                country=f'Country {i}'
            )

        self.stdout.write(self.style.SUCCESS('Location model populated successfully'))
