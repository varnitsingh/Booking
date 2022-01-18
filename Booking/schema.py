from dataclasses import dataclass

@dataclass(init=None)
class Hotel:
    hotel_name:str #
    address:str    #
    country:str
    phone:str      #?
    email:str      #?
    website:str    #?
    room_types:str #
    room_pricing:str #
    features:str   #
    facilities:str #
    description:str#
    rating:float   #
    review_score:float #
    policies:str   #
    place_of_interest_nearby:str #
    transport_nearby:str #
    attractions_nearby:str #
    url:str