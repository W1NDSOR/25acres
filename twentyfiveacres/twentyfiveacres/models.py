from django.db import models


class Property(models.Model):
    """
    reference: (99acres) https://www.99acres.com/unity-group-the-amaryllis-karol-bagh-central-delhi-npxid-r217503?advertiserIds=65041466,63639418,10809316,56662124

    few addons: price trend/comparison/insights (99acres)
    QUE: do not know if this is the place to store this or whether is
    specific to this property listing
    """

    # type of property listing can be either sell or rent.
    # NOTE: can be turned into a bool isSellType in future
    type = models.CharField(max_length=20)
    # for test purpose it is a char field
    # IMP: should be referenced to the actual user
    owner = models.CharField(max_length=50)
    # NOTE: could also be a range of prices
    amount = models.BigIntegerField()
    timeReadyToMoveIn = models.DateField()
    # QUE: not sure
    imageArray = None
    # QUE: not sure whether BHK terminology can be applied to
    # every type of property listing.
    apartmentSize = models.IntegerField()
    # string of delimiter seperated key highlights such as
    # mini theatre, restaurant, near metro station
    highlights = models.CharField(max_length=200)
    # NOTE: for now it is a char field but in future it
    # should be replaced with the field appropiate for google
    # maps place end point
    location = models.CharField(max_length=200)
    # QUE: don't know if this a correct way to store it
    # 4.2 stars
    overallRating = models.FloatField(max_length=3)
