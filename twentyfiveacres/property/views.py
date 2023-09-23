from django.shortcuts import render
from twentyfiveacres.models import Property


def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    properties = Property.objects.all()
    return render(request, "property/property_list.html", {"properties": properties})


def addProperty(request):
    """
    @desc: renders a form for adding new user
    """
    propertyFields = request.POST
    title = propertyFields.get("title")
    description = propertyFields.get("description")
    price = propertyFields.get("price")
    propertyType = propertyFields.get("property_type")
    bedrooms = propertyFields.get("bedrooms")
    bathrooms = propertyFields.get("bathrooms")
    area = propertyFields.get("area")
    status = propertyFields.get("status")
    location = propertyFields.get("location")
    availableDate = propertyFields.get("available_date")
    # just a precaution, as all the fields are required
    if (
        title
        and description
        and price
        and propertyType
        and bedrooms
        and bathrooms
        and area
        and status
        and location
        and availableDate
    ):
        Property.objects.create(
            title=title,
            description=description,
            price=price,
            propertyType=propertyType,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area=area,
            status=status,
            location=location,
            availabilityDate=availableDate,
        )
    return render(request, "property/add_property_form.html")
