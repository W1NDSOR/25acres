from django.core.management.base import BaseCommand
from twentyfiveacres.models import Contract, Property, User

class Command(BaseCommand):
    help = 'Populate the Contract model with 5 entries'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        sellers = User.objects.filter(user_type='seller')
        buyers = User.objects.filter(user_type='buyer')

        for i in range(1, 3):  # Start from 1 and go up to 5 (inclusive)
            property = properties[i - 1]  # Get the property with the same index
            seller = sellers[i - 1]  # Get the seller with the same index
            buyer = buyers[i - 1]  # Get the buyer with the same index

            Contract.objects.create(
                property=property,
                seller=seller,
                buyer=buyer,
                contract_text=f'Contract text for Property {i}',
                contract_hash=f'hash{i}',  # Change hash as needed
                contract_address=f'address{i}',  # Change address as needed
            )

        self.stdout.write(self.style.SUCCESS('Contract model populated successfully'))
