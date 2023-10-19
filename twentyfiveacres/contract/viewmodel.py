from twentyfiveacres.models import User, Property, Contract
from django.core.exceptions import ObjectDoesNotExist
from utils.hashing import hashDocument
from enum import Enum


def generateUserPropertyContractHash(user: User, property: Property):
    return hashDocument(f"{user.userHash}.{property.propertyHashIdentifier}")


class ContractStages(Enum):
    SELLER = 0
    BUYER = 1
    PAYMENT = 2
    DONE = 3


class AbstractContract:
    def __init__(self, contract: Contract):
        self.contract = contract
        self.verifiedBySeller = (
            None if contract is None else contract.sellerContract is not None
        )
        self.verifiedByBuyer = (
            None if contract is None else contract.buyerContract is not None
        )
        self.currentStage = None
        if contract is None or self.verifiedBySeller is None:
            self.currentStage = ContractStages.SELLER.value
        elif self.verifiedByBuyer is None or self.verifiedByBuyer == False:
            self.currentStage = ContractStages.BUYER.value
        else:
            self.currentStage = ContractStages.DONE.value


def getAbstractContractArray(properties):
    abstractContracts = []
    for property in properties:
        try:
            abstractContracts.append(
                AbstractContract(Contract.objects.get(property=property))
            )
        except ObjectDoesNotExist:
            abstractContracts.append(None)
    return abstractContracts
