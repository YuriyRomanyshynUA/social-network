from datetime import datetime
from datetime import timedelta
from email_validator import validate_email
from email_validator import EmailNotValidError
from flask import current_app as app
from flask import request
from flask import Blueprint
#
from social_network import db
from social_network.security import hash_password
from social_network.security import compare_passwords
from social_network.security import generate_jwt
from social_network.security import parse_user_agent
from social_network.security import generate_refresh_token
from social_network.security import jwt_auth
from social_network.other import record_activity
from social_network.errors import ApplicationError
from social_network.domain_models import User
from social_network.domain_models import UserProfile
from social_network.domain_models import RefreshToken

from .payload_models import UserSignupPayload
from .payload_models import UserSigninPayload
from .payload_models import RefreshTokenPayload


api = Blueprint("auth", __name__)


@api.route("/api/email-lookup", methods=["GET"])
@record_activity()
def email_lookup(*args, **kwargs):
    try:
        user_email = validate_email(request.args["email"]).email
    except EmailNotValidError:
        return {"value": False}

    user = (
        db.session.query(User)
        .filter(User.email==user_email)
        .filter(User.deleted_at.is_(None))
        .first()
    )

    return (
        {"status": "ok", "value": False}
        if user is None else
        {"status": "ok", "value": True}
    )


@api.route("/api/signup", methods=["POST"])
@record_activity()
def signup(*args, **kwargs):
    now = datetime.now()
    user_payload = UserSignupPayload(**request.get_json())

    # === does the user with the received email exist ===

    existing_user = (
        db.session.query(User)
        .filter(User.email==user_payload.email)
        .filter(User.deleted_at.is_(None))
        .first()
    )

    if existing_user is not None:
        raise ApplicationError(
            f"User with email - {user_payload.email} - already exist!",
            code=400
        )

    # === hashing password and creating new user ===

    hashed_passw = hash_password(user_payload.password.get_secret_value())

    new_user = User(
        email=user_payload.email,
        password=hashed_passw,
        created_at=now
    )
    new_user.profile = UserProfile(
        first_name = user_payload.first_name,
        last_name = user_payload.last_name,
        full_name = f"{user_payload.first_name} {user_payload.last_name}",
        sex = user_payload.sex,
        country = user_payload.country,
        city = user_payload.city,
        birthday = user_payload.birthday,
        phone = user_payload.phone,
        created_at = now
    )

    db.session.add(new_user)
    db.session.commit()

    return {"status": "ok", "value": new_user.id}


@api.route("/api/signin", methods=["POST"])
@record_activity()
def signin(*args, **kwargs):
    ua_header = request.headers.get("User-Agent", "")
    user_agent = parse_user_agent(ua_header)

    signin_payload = UserSigninPayload(**request.get_json())

    # === does the user with the received email exist ===

    user = (
        db.session.query(User)
        .filter(User.email==signin_payload.email)
        .filter(User.deleted_at.is_(None))
        .first()
    )
        
    if user is None:
        raise ApplicationError(
            f"Access denied. User with email - {signin_payload.email} - does not exist!",
            code=403
        )

    # === 

    if compare_passwords(signin_payload.password.get_secret_value(), user.password):

        # the password is correct; generating jwt and refresh tokens
        
        now = datetime.now()
        jwt_token_ttl = app.config["JWT_TOKEN_POLICY"]["TOKEN_EXPIRES_IN"]
        refresh_token_ttl = app.config["JWT_TOKEN_POLICY"]["REFRESH_TOKEN_EXPIRES_IN"]
        jwt_token_expires_at = now + timedelta(seconds=jwt_token_ttl)
        refresh_token_expires_at = now + timedelta(seconds=refresh_token_ttl)

        refresh_token = RefreshToken(
            token=generate_refresh_token(),
            exp=refresh_token_expires_at,
            os=user_agent["os"],
            device=user_agent["device"],
            browser=user_agent["browser"],
            created_at=now
        )

        db.session.add(refresh_token)
        db.session.commit()

        jwt_payload = {
            "usrid": user.id,
            "usrrole": user.security_role,
            "exp": jwt_token_expires_at,
            **user_agent
        }
        jwt_token = generate_jwt(
            jwt_payload,
            app.config["JWT_TOKEN_POLICY"]
        )

        return {
            "token": jwt_token,
            "refresh_token": refresh_token.token,
            "expires_at": int(jwt_token_expires_at.timestamp() * 1000),
            "refresh_token_expires_at": int(refresh_token_expires_at.timestamp() * 1000)
        }, 200

    else:
        raise ApplicationError(
            "Access denied. Inccorrect password",
            code=403
        )


@api.route("/api/refresh-token", methods=["POST"])
@jwt_auth(can_be_expired=True)
@record_activity()
def refresh_jwt_token(*args, **kwargs):
    now = datetime.now()

    user = kwargs["user"]  # from the jwt_auth decorator
    user_agent = kwargs["user_agent"]  # from the jwt_auth decorator
    token_payload = RefreshTokenPayload(**request.get_json())

    # === does the refresh token exist in db ===

    refresh_token = (
        db.session.query(RefreshToken)
        .filter(RefreshToken.token == token_payload.refresh_token.get_secret_value())
        .filter(RefreshToken.deleted_at.is_(None))
        .first()
    )

    if refresh_token is None:
        raise ApplicationError("Invalid refresh token", code=403)

    # === is the refresh token expired ===

    if refresh_token.exp < now:
        refresh_token.deleted_at = now
        db.session.commit()
        raise ApplicationError("Refresh token expired", code=403)

    # === generating new jwt token ===

    jwt_token_ttl = app.config["JWT_TOKEN_POLICY"]["TOKEN_EXPIRES_IN"]
    jwt_token_expires_at = now + timedelta(seconds=jwt_token_ttl)

    jwt_payload = {
        "usrid": user.id,
        "usrrole": user.security_role,
        "exp": jwt_token_expires_at,
        **user_agent
    }
    jwt_token = generate_jwt(
        jwt_payload,
        app.config["JWT_TOKEN_POLICY"]
    )

    return {
        "token": jwt_token,
        "expires_at": int(jwt_token_expires_at.timestamp() * 1000),
    }, 200
