from pydantic import BaseModel
from typing import Optional, List


class PequeSchema(BaseModel):
    position: Optional[str]
    title: Optional[str]
    place_id: Optional[str]
    data_id: Optional[str]
    data_cid: Optional[str]
    reviews_link: Optional[str]
    photos_link: Optional[str]
    gps_coordinates: Optional[str]
    place_id_search: Optional[str]
    provider_id: Optional[str]
    rating: Optional[str]
    reviews: Optional[str]
    unclaimed_listing: Optional[str]
    type: Optional[str]
    types: Optional[str]
    type_id: Optional[str]
    type_ids: Optional[str]
    address: Optional[str]
    open_state: Optional[str]
    hours: Optional[str]
    operating_hours: Optional[str]
    phone: Optional[str]
    extensions: Optional[str]
    service_options: Optional[str]
    thumbnail: Optional[str]
    serpapi_thumbnail: Optional[str]
    price: Optional[str]
    order_online: Optional[str]
    unsupported_extensions: Optional[str]
    website: Optional[str]
    description: Optional[str]



class PequeRegistroRequest(BaseModel):
    nombre: str
    correo: str
    whatsapp: str
    tipo_negocio: str
    ubicacion: str  # Ejemplo: "-17.6822538,-63.1525464"

class PequeRegistroResponse(BaseModel):
    nearby_peques: List[dict]
