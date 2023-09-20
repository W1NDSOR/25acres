# from django.db.models import (
#     Model,
#     AutoField,
#     ForeignKey,
#     CASCADE,
#     TextField,
#     DateTimeField,
#     CharField,
# )
# from twentyfiveacres.models import User, Property, Location


# # Remove this (should only be in main models.py)

# # Contract Model (with Blockchain Integration)
# class Contract(Model):
#     contractId = AutoField(primary_key=True)
#     property = ForeignKey(Property, on_delete=CASCADE)
#     seller = ForeignKey(User, related_name="seller_contracts", on_delete=CASCADE)
#     buyer = ForeignKey(User, related_name="buyer_contracts", on_delete=CASCADE)
#     contractText = TextField()
#     contractHash = CharField(
#         max_length=64
#     )  # Hash or identifier for blockchain verification
#     contract_address = CharField(
#         max_length=255, blank=True, null=True
#     )  # Blockchain contract address (if applicable)
#     createdAt = DateTimeField(auto_now_add=True)
#     updatedAt = DateTimeField(auto_now=True)
