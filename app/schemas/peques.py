from pydantic import BaseModel
from typing import Optional, List, Dict, Union

class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float

class PequeEmpresaResponse(BaseModel):
    position: Optional[int]
    title: Optional[str]
    place_id: Optional[str]
    data_id: Optional[str]
    data_cid: Optional[str]
    reviews_link: Optional[str]
    photos_link: Optional[str]
    gps_coordinates: Optional[GPSCoordinates]
    place_id_search: Optional[str]
    provider_id: Optional[str]
    rating: Optional[float]
    reviews: Optional[int]
    unclaimed_listing: Optional[Union[str, bool]]
    type: Optional[str]
    types: Optional[List[str]]
    type_id: Optional[str]
    type_ids: Optional[List[str]]
    address: Optional[str]
    open_state: Optional[str]
    hours: Optional[str]
    operating_hours: Optional[Dict[str, str]]
    phone: Optional[str]
    extensions: Optional[str]
    service_options: Optional[List[Dict[str, List[str]]]]
    thumbnail: Optional[str]
    serpapi_thumbnail: Optional[str]
    price: Optional[str]
    order_online: Optional[str]
    unsupported_extensions: Optional[str]
    website: Optional[str]
    description: Optional[str]
