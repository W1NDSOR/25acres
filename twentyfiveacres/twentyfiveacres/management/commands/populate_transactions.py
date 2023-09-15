from django.core.management.base import BaseCommand
from twentyfiveacres.models import Transaction, Property, User

class Command(BaseCommand):
    help = 'Populate the Transaction model with 5 entries'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        buyers = User.objects.filter(user_type='buyer')
        sellers = User.objects.filter(user_type='seller')

        for i in range(1, 3):  # Start from 1 and go up to 5 (inclusive)
            property = properties[i - 1]  # Get the property with the same index
            buyer = buyers[i - 1]  # Get the buyer with the same index
            seller = sellers[i - 1]  # Get the seller with the same index

            Transaction.objects.create(
                property=property,
                buyer=buyer,
                seller=seller,
                transaction_type='booking',  # Change transaction type as needed
                transaction_date='2023-09-15',  # Change transaction date as needed
                amount=100000 + i * 20000  # Change the amount as needed
            )

        self.stdout.write(self.style.SUCCESS('Transaction model populated successfully'))
