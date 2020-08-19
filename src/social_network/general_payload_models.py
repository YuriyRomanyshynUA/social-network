from pydantic import BaseModel
from pydantic import validator
from social_network.domain_models import SecurityRoles
from social_network.settings import PAGINATION_POLICY




class PaginationPayload(BaseModel):
    limit: int = PAGINATION_POLICY["LIMIT"]
    page: int = 1

    @validator("limit")
    def limit_validator(cls, limit):
        assert limit >= 1, "limit cannot be less than 1"
        limit = limit if limit <= PAGINATION_POLICY["LIMIT"] else PAGINATION_POLICY["LIMIT"]
        return limit

    @validator("page")
    def page_validator(cls, page):
        assert page > 0, "page cannot be less than 1"
        return page



class JwtTokenPayload(BaseModel):
    usrid: int
    usrrole: SecurityRoles
    exp: int
    os: str
    device: str
    browser: str
