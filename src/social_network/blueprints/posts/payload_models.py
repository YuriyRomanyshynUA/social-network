from typing import Optional
from pydantic import BaseModel

from social_network.general_payload_models import PaginationPayload


class PostCreatePayload(BaseModel):
    title: str
    content: str


class PostLookupPayload(PaginationPayload):
    user_full_name: Optional[str]
    title: Optional[str]
    content: Optional[str]


class UserPostsLookupPayload(PaginationPayload):
    user_id: Optional[str]
