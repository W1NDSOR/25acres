# Contracts Model

'''
    class Contract(models.Model):
        contract_id = models.AutoField(primary_key=True)
        property = models.ForeignKey(Property, on_delete=models.CASCADE)
        seller = models.ForeignKey(User, related_name="seller_contracts", on_delete=models.CASCADE)
        buyer = models.ForeignKey(User, related_name="buyer_contracts", on_delete=models.CASCADE)
        contract_text = models.TextField()
        contract_hash = models.CharField(max_length=64)
        contract_address = models.CharField(max_length=255, blank=True, null=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

'''

from django.core.management.base import BaseCommand
from twentyfiveacres.models import User, Property, Contract
import random

class Command(BaseCommand):
    help = 'Populate the **table** with sample data'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        buyers = User.objects.filter(user_type='buyer')
        sellers = User.objects.filter(user_type='seller')
        print('Populating Contract model...')

        for i in range(1, 3):
            property_instance = random.choice(properties)  # Select a random property instance
            buyer = random.choice(buyers)  # Select a random buyer
            seller = random.choice(sellers)  # Select a random seller

            Contract.objects.create(
                property=property_instance,
                buyer=buyer,
                seller=seller,
                contract_text='This is a sample contract text',  # Change contract text as needed
                contract_hash='This is a sample contract hash',  # Change contract hash as needed
                contract_address='This is a sample contract address'  # Change contract address as needed
            )

        self.stdout.write(self.style.SUCCESS('Contract model populated successfully'))
