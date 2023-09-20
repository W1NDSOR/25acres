# Property Model

'''
    class Property(models.Model):
    property_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=100)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("for_sale", "For Sale"), ("for_rent", "For Rent"), ("sold", "Sold"), ("rented", "Rented")])
    availability_date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

'''

from django.core.management.base import BaseCommand
from twentyfiveacres.models import Property, Location

class Command(BaseCommand):
    help = 'Populate the **table** with sample data'

    def handle(self, *args, **kwargs):
        location = Location.objects.first() 
        print('Populating Property model...')

        for i in range(1, 6):  
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
