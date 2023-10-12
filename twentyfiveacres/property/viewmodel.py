from utils.hashing import hashDocument


def generatePropertyHash(
    ownershipDocumentHash,
    title,
    description,
    price,
    bedrooms,
    bathrooms,
    area,
    status,
    location,
    availabilityDate,
):
    """
    @desc: generates a unique hash identifier for a property based on its details
    @return {str} hash: A unique SHA-256 hash identifier for the property
    """
    return hashDocument(
        f"{ownershipDocumentHash}.{title}.{description}.{price}.{bedrooms}.{bathrooms}.{area}.{status}.{location}.{availabilityDate}"
    )
