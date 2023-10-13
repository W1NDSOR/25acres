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
)

# Create your views here.

def paymentGateway(request):
    contract = Contract.objects.get(id=request.GET.get("id"))
    property = Property.objects.get(id=contract.property_id)

    return render(request, "paymentGateway.html", context={"property": property, "contract": contract})

def cardDetails(request):
    contract = Contract.objects.get(id=request.GET.get("id"))
    property = Property.objects.get(id=contract.property_id)
    context = {
        "title": "Payment Gateway",
        "content": "Payment Gateway",
        "id": contract.id,
        "property_id": contract.property_id,
        "buyer_id": contract.buyerContract_id,
        "seller_id": contract.sellerContract_id,
        "price": property.price,
    }
    if request.method == "POST" and request.POST.get("action") == "Card Details":
        cardNumber = request.get("cardNumber")
        expirationDate = request.get("expirationDate")
        cvv = request.get("cvv")
        cardHolderName = request.get("cardHolderName")
        amount = request.get("currentBid")

        # remove printing later, and just keep a hash or return statment
        print(cardNumber, expirationDate, cvv, cardHolderName, amount)

def pay(request):
    contract = Contract.objects.get(id=request.GET.get("id"))
    buyer = User.objects.get(id=contract.buyerContract_id)
    seller = User.objects.get(id=contract.sellerContract_id)
    print(request.method)
    if request.method == "POST":
        print("Reached paymentGateway 2")
        if request.POST.get("action") == "Pay":
            messages.success(request, "Payment successful")
            buyer.wallet -= property.currentBid
            seller.wallet += property.currentBid
            return HttpResponse("Payment successful")
        else:
            messages.error(request, "Something went wrong")
            return HttpResponse("Something went wrong")