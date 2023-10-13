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
    # needs fixing
    contract = Contract.objects.get(id=request.GET.get("id"))
    property = Property.objects.get(id=contract.property_id)
    buyer = User.objects.get(id=contract.buyerContract_id)
    seller = User.objects.get(id=contract.sellerContract_id)

    context = {
        "title": "Payment Gateway",
        "content": "Payment Gateway",
        "id": contract.id,
        "property_id": contract.property_id,
        "buyer_id": contract.buyerContract_id,
        "seller_id": contract.sellerContract_id,
        "price": property.price,
    }

    print("Reached paymentGateway 1")
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


    return render(request, "paymentGateway.html", context={})