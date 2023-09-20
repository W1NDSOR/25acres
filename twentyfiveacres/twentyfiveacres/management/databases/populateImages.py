# Image Model

'''
    class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

'''

from django.core.management.base import BaseCommand
from twentyfiveacres.models import User, Property, Image

class Command(BaseCommand):
    help = 'Populate the **table** with sample data'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        users = User.objects.all()
        print('Populating Image model...')

        for i in range(1, 6):  # Start from 1 and go up to 5 (inclusive)
            property = properties[i - 1]  # Get the property with the same index
            user = users[i - 1] if i % 2 == 0 else None  # Assign user every 2 iterations

            Image.objects.create(
                property=property,
                user=user,
                image_url=f'https://example.com/images/image{i}.jpg',  # Change URL as needed
            )

        self.stdout.write(self.style.SUCCESS('Image model populated successfully'))
