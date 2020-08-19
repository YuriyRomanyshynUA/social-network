from flask import request
from flask import Blueprint
from sqlalchemy import func
#
from social_network import db
from social_network.errors import ApplicationError
from social_network.security import jwt_auth
from social_network.other import record_activity
from social_network.domain_models import UserProfile
from social_network.domain_models import Post
#
from .payload_models import UsersLookupPayload


api = Blueprint("users", __name__)


@api.route("/api/user/<int:user_id>", methods=["GET"])
@jwt_auth()
@record_activity()
def get_user_profile(user_id, *args, **kwargs):

    user_profile, posts_count = (
        db.session.query(UserProfile, func.count(Post.id))
        .outerjoin(Post)
        .filter(UserProfile.user_id == user_id)
        .filter(UserProfile.deleted_at.is_(None))
        .filter(Post.deleted_at.is_(None))
        .group_by(UserProfile.id)
        .first()
    )

    if user_profile is None:
        raise ApplicationError("User does not exist", code=404)

    return {
        "status": "ok",
        "data": [{
            "id": user_profile.user_id,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "full_name": user_profile.full_name,
            "sex": user_profile.sex,
            "city": user_profile.city,
            "country": user_profile.country,
            "birthday": user_profile.birthday,
            "signup_at": int(user_profile.created_at.timestamp() * 1000),
            "posts_count": posts_count
        }]
    }


@api.route("/api/users/lookup", methods=["GET"])
@jwt_auth()
@record_activity()
def users_lookup(*args, **kwargs):
    lookup_payload = UsersLookupPayload(**request.args)

    criteria = [
        UserProfile.deleted_at.is_(None)
    ]
    
    if lookup_payload.full_name:
        criteria.append(
            UserProfile.full_name.like(f"%{lookup_payload.full_name}%")
        )

    if lookup_payload.country:
        criteria.append(
            UserProfile.country.like(f"%{lookup_payload.country}%")
        )

    if lookup_payload.city:
        criteria.append(
            UserProfile.city.like(f"%{lookup_payload.city}%")
        )

    offset = (lookup_payload.page - 1) * lookup_payload.limit

    total_users_count = (
        db.session.query(UserProfile)
        .filter(*criteria)
        .count()
    )

    total_pages_count = (
        int(total_users_count / lookup_payload.limit)
        + int((total_users_count % lookup_payload.limit) != 0)
    )

    if lookup_payload.page > total_pages_count:
        return {
            "status": "ok",
            "data": [],
            "total_posts_count": total_users_count,
            "total_pages_count": total_pages_count,
            "has_more": False,
            "query": lookup_payload.dict()
        }

    users = (
        db.session.query(UserProfile, func.count(Post.id))
        .outerjoin(Post)
        .filter(*criteria)
        .group_by(UserProfile.id)
        .limit(lookup_payload.limit)
        .offset(offset)
        .all()
    )

    data = [{
        "id": usr.user_id,
        "first_name": usr.first_name,
        "last_name": usr.last_name,
        "full_name": usr.full_name,
        "sex": usr.sex,
        "city": usr.city,
        "country": usr.country,
        "birthday": usr.birthday,
        "signup_at": int(usr.created_at.timestamp() * 1000),
        "posts_count": posts_count
    } for (usr, posts_count) in users]


    return {
        "status": "ok",
        "data": data,
        "total_users_count": total_users_count,
        "total_pages_count": total_pages_count,
        "has_more": False,
        "query": lookup_payload.dict()
    }
