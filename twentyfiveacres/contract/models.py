from django.db.models import (
    Model,
    AutoField,
    ForeignKey,
    CASCADE,
    TextField,
    DateTimeField,
    CharField,
)
from user.models import User
from property.models import Property

# Contract Model (with Blockchain Integration)
class Contract(Model):
    contract_id = AutoField(primary_key=True)
    property = ForeignKey(Property, on_delete=CASCADE)
    seller = ForeignKey(User, related_name="seller_contracts", on_delete=CASCADE)
    buyer = ForeignKey(User, related_name="buyer_contracts", on_delete=CASCADE)
    contract_text = TextField()
    contract_hash = CharField(
        max_length=64
    )  # Hash or identifier for blockchain verification
    contract_address = CharField(
        max_length=255, blank=True, null=True
    )  # Blockchain contract address (if applicable)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
