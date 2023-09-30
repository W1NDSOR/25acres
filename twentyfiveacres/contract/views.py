from django.shortcuts import render
from twentyfiveacres.models import Contract

def listContracts(request):
    contracts = Contract.objects.all()
    return render(request, "contract_list.html", {"contracts": contracts})
