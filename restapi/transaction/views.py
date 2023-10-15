from django.contrib import messages
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from restapi.models import User, Property, Contract, SellerContract, BuyerContract

class PaymentGatewayView(APIView):
    def post(self, request):
        try:
            action = request.data.get("action")
            if action == "Pay":
                contract_id = request.data.get("id")
                contract = Contract.objects.get(id=contract_id)
                property = Property.objects.get(id=contract.property_id)
                buyer = User.objects.get(id=contract.buyerContract_id)
                seller = User.objects.get(id=contract.sellerContract_id)

                # Perform payment logic here
                # Example: buyer.wallet -= property.currentBid, seller.wallet += property.currentBid

                messages.success(request, "Payment successful")
                return HttpResponse("Payment successful")
            else:
                messages.error(request, "Something went wrong")
                return HttpResponse("Something went wrong")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
