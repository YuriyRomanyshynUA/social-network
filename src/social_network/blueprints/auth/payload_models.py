from datetime import date
from typing import Union
from pydantic import BaseModel
from pydantic import validator
from pydantic import EmailStr
from pydantic import SecretStr

from social_network.domain_models import Sex
from social_network.security import validate_password
from social_network.settings import PASSWORD_FORMAT_POLICY



class UserSignupPayload(BaseModel):
    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str
    sex: Union[Sex, None]
    country: Union[str, None]
    city: Union[str, None]
    birthday: Union[date, None]
    phone: Union[str, None]

    @validator("password")
    def password_validator(cls, password):
        validate_password(password.get_secret_value(), PASSWORD_FORMAT_POLICY)
        return password


class UserSigninPayload(BaseModel):
    email: EmailStr
    password: SecretStr


class RefreshTokenPayload(BaseModel):
    refresh_token: SecretStr
