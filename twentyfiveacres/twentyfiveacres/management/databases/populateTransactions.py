# Transactions Model

'''
    class Transaction(models.Model):
        transaction_id = models.AutoField(primary_key=True)
        property = models.ForeignKey(Property, on_delete=models.CASCADE)
        buyer = models.ForeignKey(User, related_name='buyer_transactions', on_delete=models.CASCADE)
        seller = models.ForeignKey(User, related_name='seller_transactions', on_delete=models.CASCADE)
        transaction_type = models.CharField(max_length=20, choices=[("booking", "Booking"), ("down_payment", "Down Payment"), ("full_payment", "Full Payment"), ("rent", "Rent")])
        transaction_date = models.DateField()
        amount = models.DecimalField(max_digits=10, decimal_places=2)

'''

from django.core.management.base import BaseCommand
from twentyfiveacres.models import Transaction, Property, User

class Command(BaseCommand):
    help = 'Populate the **table** with 5 entries'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        buyers = User.objects.filter(user_type='buyer')
        sellers = User.objects.filter(user_type='seller')
        print('Populating Transaction model...')
        
        for i in range(1, 3):  
            property = properties[i - 1] 
            buyer = buyers[i - 1] if i <= 5 else buyers[i - 6]
            seller = sellers[i - 1] if i <= 5 else sellers[i - 6]

            Transaction.objects.create(
                property=property,
                buyer=buyer,
                seller=seller,
                transaction_type='booking', 
                transaction_date='2023-09-15', 
                amount=100000 + i * 20000  
            )

        self.stdout.write(self.style.SUCCESS('Transaction model populated successfully'))
