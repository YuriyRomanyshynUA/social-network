from flask import current_app as app
from flask import request
from flask import Blueprint
#
from social_network import db
from social_network.domain_models import UserProfile
from social_network.payload_models import UserLookupPayload
from social_network.security import jwt_auth



api = Blueprint("users", __name__)


@api.route("/api/users/lookup")
@jwt_auth()
def users_lookup(*args, **kwargs):
    pass
    # lookup_payload = UserLookupPayload(**request.args)

    # criteria = []
    
    # if lookup_payload.full_name:
    #     criteria.append(
    #         UserProfile.full_name.like(f"%{lookup_payload.full_name}%")
    #     )

    # if lookup_payload.country:
    #     criteria.append(
    #         UserProfile.country.like(f"%{lookup_payload.country}%")
    #     )

    # if lookup_payload.city:
    #     criteria.append(
    #         UserProfile.city.like(f"%{lookup_payload.city}%")
    #     )

    # total_user_count = (
    #     db.session.query(UserProfile)
    #     .filter(*criteria)
    #     .count()
    # )

    # pages_count = (
    #     int(total_user_count / lookup_payload.limit)
    #     + int((total_user_count % lookup_payload.limit) != 0)
    # )

    # if lookup_payload.page >= pages_count:
    #     return {
    #         "status": "ok",
    #         "data": [],
    #         "pages_count": pages_count,
    #         "has_more": False,
    #         "page": lookup_payload.page,
    #         "limit": lookup_payload.limit
    #     }

    # users = (
    #     db.session.query(UserProfile)
    #     .filter(*criteria)
    #     .all()
    # )

        
        
