from typing import Optional
from social_network.general_payload_models import PaginationPayload


class UsersLookupPayload(PaginationPayload):
    full_name: Optional[str]
    country: Optional[str]
    city: Optional[str]
