import requests

def geocode_location(location):
    # URL for geocoding API (forward geocoding)
    geocoding_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    
    # Make the HTTP GET request to the geocoding API
    response = requests.get(geocoding_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract latitude and longitude from the response
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
    else:
        print("Geocoding request failed")
    
    return None

def reverse_geocode(lat, lon):
    # URL for reverse geocoding API
    reverse_geocoding_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    
    # Make the HTTP GET request to the reverse geocoding API
    response = requests.get(reverse_geocoding_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract the address from the response
            address = data.get("display_name", "Address not found")
            return address
    else:
        print("Reverse geocoding request failed")
    
    return None

if __name__ == "__main__":
    # Example usage:
    location = "Govindpuri, Delhi"
    
    # Geocode the location to get coordinates
    coordinates = geocode_location(location)
    if coordinates:
        print(f"Coordinates for '{location}': Latitude = {coordinates[0]}, Longitude = {coordinates[1]}")
        
        # Reverse geocode the coordinates to get an address
        address = reverse_geocode(coordinates[0], coordinates[1])
        if address:
            print(f"Reverse geocoded address: {address}")
