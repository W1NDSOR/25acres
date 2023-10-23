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


# I don't know the point of this.
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
    if request.method == "POST":
        contract = Contract.objects.get(id=request.POST.get("contract_id"))
        property = Property.objects.get(propertyId=contract.property_id)

        buyer = property.bidder
        seller = property.owner

        buyer.wallet = buyer.wallet - property.currentBid
        buyer.save()
        transaction = Transaction.objects.create(
            user=buyer,
            withPortal=False,
            other=seller,
            amount=property.currentBid,
            credit=False,
            debit=True,
        )
        transaction.save()

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

        property.owner = buyer
        if property.status in ("for_sell", "For Sell"):
            property.status = "Sold"
        elif property.status in ("for_rent", "For Rent"):
            property.status = "Rented"
        property.save()

        return HttpResponse("Payment successful")
    else:
        return HttpResponse("Only method = POST is acceptable")
