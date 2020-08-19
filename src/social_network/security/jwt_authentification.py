import jwt
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidTokenError
from datetime import datetime
from datetime import timedelta
from functools import wraps

from flask import current_app as app
from flask import request

from .security_utils import parse_user_agent
from social_network import db
from social_network.domain_models import User
from social_network.general_payload_models import JwtTokenPayload
from social_network.errors import ApplicationError


__all__ = ["jwt_auth", "generate_jwt", "verify_jwt"]


def jwt_auth(can_be_expired=False):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            token = request.headers.get("Authorization")
            ua_header = request.headers.get("User-Agent", "")
            user_agent = parse_user_agent(ua_header)
            user = _jwt_auth(token, user_agent, can_be_expired)
            kwargs.update({"user": user, "user_agent": user_agent})
            return func(*args, **kwargs)
        return decorator
    return wrapper


def _jwt_auth(token, user_agent, can_be_expired):

    if token is None or not token.startswith("Bearer "):
        raise ApplicationError("Access denied. Unvalid bearer", code=403)

    token = token.replace("Bearer ", "").strip()

    try:
        token_payload = JwtTokenPayload(**verify_jwt(token, app.config["JWT_TOKEN_POLICY"]))
    except ExpiredSignatureError:
        if not can_be_expired:
            raise ApplicationError("Access denied. Token expired", code=403)
    except InvalidTokenError:
        raise ApplicationError("Access denied. Unvalid bearer", code=403)

    if (
        user_agent["os"] != token_payload.os
        or user_agent["device"] != token_payload.device
        or user_agent["browser"] != token_payload.browser
    ):
        raise ApplicationError("Access denied.", code=403)

    user = (
        db.session.query(User)
        .filter(User.id == token_payload.usrid)
        .first()
    )

    if user is None:
        app.logger.error("WARNING! jwt token is valid but user does not exists!")
        raise ApplicationError("Access denied", code=403)
        
    if user.security_role != token_payload.usrrole:
        app.logger.error("WARNING! jwt token is valid but user role probably was changed!")
        raise ApplicationError("Access denied", code=403)

    return user


def generate_jwt(payload, policy):
    exp = payload.pop(
        "exp",
        datetime.now() + timedelta(seconds=policy["TOKEN_EXPIRES_IN"])
    )
    payload = dict(**payload, exp=exp)
    return jwt.encode(
        payload,
        policy["SECRET"],
        algorithm=policy["ALGORITM"]
    ).decode()


def verify_jwt(token, policy):
    return jwt.decode(
        token,
        policy["SECRET"],
        algorithms=policy["ALGORITM"]
    )
