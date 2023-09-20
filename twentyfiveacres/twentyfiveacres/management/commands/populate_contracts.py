# from django.db import models

# # User Model
# class User(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=100, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=20)
#     user_type = models.CharField(max_length=20, choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")])

from django.core.management.base import BaseCommand
from twentyfiveacres.models import Property, User, Contract
import random

class Command(BaseCommand):
    help = 'Populate the Contract model with 5 entries'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        buyers = User.objects.filter(user_type='buyer')
        sellers = User.objects.filter(user_type='seller')
        # print(properties)
        # print(buyers)
        # print(sellers)

        print('Populating Contract model...')
        

        for i in range(1, 3):

            property_instance = random.choice(properties)  # Select a random property instance
            buyer = random.choice(buyers)  # Select a random buyer
            seller = random.choice(sellers)  # Select a random seller
            print(property_instance)
            print(buyer)
            print(seller)

            Contract.objects.create(
                property=property_instance,
                buyer=buyer,
                seller=seller,
                contract_text='This is a sample contract text',  # Change contract text as needed
                contract_hash='This is a sample contract hash',  # Change contract hash as needed
                contract_address='This is a sample contract address'  # Change contract address as needed
            )

        self.stdout.write(self.style.SUCCESS('Contract model populated successfully'))
