from django.shortcuts import render
from .models import Contract


def listContracts(request):
    contracts = Contract.objects.all()
    return render(request, "contract_list.html", {"contracts": contracts})
