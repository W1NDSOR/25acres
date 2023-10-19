from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from twentyfiveacres.models import (
    User,
    Property,
    Contract,
    SellerContract,
    BuyerContract,
    Transaction,
)

# Create your views here.


def paymentGateway(request, propertyId):
    contract = Contract.objects.get(property=propertyId)
    property = Property.objects.get(pk=propertyId)
    return render(
        request, "paymentGateway.html", {"contract": contract, "property": property}
    )


def cardDetails(request):
    print("Card Details Function")
    # contract = Contract.objects.get(id=request.GET.get("id"))
    # property = Property.objects.get(id=contract.property_id)
    # context = {
    #     "title": "Payment Gateway",
    #     "content": "Payment Gateway",
    #     "id": contract.id,
    #     "property_id": contract.property_id,
    #     "buyer_id": contract.buyerContract_id,
    #     "seller_id": contract.sellerContract_id,
    #     "price": property.price,
    # }
    print(request.method)
    if request.method == "POST":
        cardNumber = request.get("cardNumber")
        expirationDate = request.get("expirationDate")
        cvv = request.get("cvv")
        cardHolderName = request.get("cardHolderName")
        amount = request.get("currentBid")

        # remove printing later, and just keep a hash or return statment
        print(cardNumber, expirationDate, cvv, cardHolderName, amount)
        return HttpResponse("Payment successful")
    else:
        return HttpResponse("Something went wrong")


def pay(request):
    print("Paying")
    if request.method == "POST":
        print("Entered Method Post")
        contract_id = request.POST.get("contract_id")
        contract = Contract.objects.get(id=contract_id)
        print(contract_id)
        property = Property.objects.get(propertyId=contract.property_id)
        print(property)
        buyer = User.objects.get(id=property.bidder_id)
        seller = User.objects.get(id=property.owner_id)
        print("Contract, Buyer and Seller found")
        # reduce the balance of the buyer
        buyer.wallet = buyer.wallet - property.currentBid
        buyer.save()
        print("Buyer balance reduced")
        transaction = Transaction.objects.create(
            user=buyer,
            withPortal=False,
            other=seller,
            amount=property.currentBid,
            credit=False,
            debit=True,
        )
        transaction.save()
        # increase the balance of the seller
        seller.wallet = seller.wallet + property.currentBid
        seller.save()
        print("Seller balance increased")
        transaction = Transaction.objects.create(
            user=seller,
            withPortal=False,
            other=buyer,
            amount=property.currentBid,
            credit=True,
            debit=False,
        )
        transaction.save()
        return HttpResponse("Payment successful")
    #     if request.POST.get("action") == "Pay":
    #     else:
    # #         messages.error(request, "Something went wrong")
    #         return HttpResponse("Something went wrong")
