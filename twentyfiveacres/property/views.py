from django.shortcuts import render
from twentyfiveacres.models import Property

def propertyList(request):
    properties = Property.objects.all()
    return render(request, 'property/property_list.html', {'properties': properties})