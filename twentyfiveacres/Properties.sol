// PropertyListing.sol
pragma solidity ^0.8.0;

contract PropertyListing {
    struct Property {
        string title;
        string description;
        int price;
        int bedrooms;
        int bathrooms;
        int area;
        string status;
        string location;
        string availableDate;
        address owner;
        bool listed;
    }

    Property[] public properties;

    function listProperty(
        string memory title,
        string memory description,
        int price,
        int bedrooms,
        int bathrooms,
        int area,
        string memory status,
        string memory location,
        string memory availableDate
    ) public {
        properties.push(Property({
            title: title,
            description: description,
            price: price,
            bedrooms: bedrooms,
            bathrooms: bathrooms,
            area: area,
            status: status,
            location: location,
            availableDate: availableDate,
            owner: msg.sender,
            listed: true
        }));
    }
}
