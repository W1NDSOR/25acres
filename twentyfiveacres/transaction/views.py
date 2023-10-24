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
from utils.mails import generateGcmOtp, sendMail
# Create your views here.
from os import urandom

secretKey = urandom(16)

def paymentGateway(request, propertyId):

    if request.method == 'GET':
        # Generate a 6-digit OTP
        user = User.objects.get(username=request.user.username)
        roll = user.rollNumber
        roll = str(roll)
        otp = generateGcmOtp(secretKey, roll.encode())
        
        # Save the OTP in the session for later verification
        request.session['otp'] = str(otp)

        # Send the OTP via email
        # TODO: Get the user's email from the user model or from the session
        sendMail(
                subject="The payment is under process..",
                message=f"Your otp is {otp}",
                recipientEmails=[user.email],
            )

    contract = Contract.objects.get(property=propertyId)
    property = Property.objects.get(pk=propertyId)
    return render(
        request, "paymentGateway.html", {"contract": contract, "property": property}
    )



# def paymentGateway(request, propertyId):
#     contract = Contract.objects.get(property=propertyId)
#     property = Property.objects.get(pk=propertyId)
#     return render(
#         request, "paymentGateway.html", {"contract": contract, "property": property}
#     )



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
        user_otp = request.get('otp')

        # Retrieve the saved OTP from the session
        saved_otp = request.session.get('otp')
        print("Something else here as well")
        print(user_otp)
        print(saved_otp)
        # Verify the OTP
        if user_otp == saved_otp:
            print("OTPP VERIFICATION DONE FOR THE PAYMENT")
        if user_otp != saved_otp:
            return HttpResponse("Invalid OTP, please try again.")
        
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


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

def pay(request):
    if request.method == "POST":
        contract_id = request.POST.get("contract_id")
        user_otp = request.POST.get('otp')

        # Retrieve the saved OTP from the session
        saved_otp = request.session.get('otp')
        print(user_otp)
        print(saved_otp)
        # Verify the OTP
        if user_otp != saved_otp:
            messages.error(request, "Invalid OTP, please try again.")
            return redirect('paymentGateway.html', contract_id=contract_id)  # Assuming 'payment_page' is the name of your payment page's URL

        contract = Contract.objects.get(id=contract_id)
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
