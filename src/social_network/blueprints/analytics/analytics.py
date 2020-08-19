from flask import request
from flask import Blueprint
from sqlalchemy import func
#
from social_network import db
from social_network.security import jwt_auth
from social_network.other import record_activity
from social_network.domain_models import Like
from social_network.domain_models import Post
from social_network.domain_models import UserProfile
#
from .payload_models import AggregationPeriod
from .payload_models import LikesAggregationPayload


api = Blueprint("analytics", __name__)


@api.route("/api/analytics/likes-aggregation", methods=["GET"])
@jwt_auth()
@record_activity()
def get_like_aggregation(*args, **kwargs):

    user = kwargs["user"]  # from the jwt_auth decorator
    payload = LikesAggregationPayload(**request.args)

    criteria = [
        UserProfile.user_id == user.id,
        UserProfile.deleted_at.is_(None),
        Post.deleted_at.is_(None),
        Like.deleted_at.is_(None),
        Like.created_at.between(payload.date_from, payload.date_to)
    ]

    if payload.agg_period == AggregationPeriod.by_day:
        data = _likes_aggregation_by_day(criteria)

    if payload.agg_period == AggregationPeriod.by_month:
        data = _likes_aggregation_by_month(criteria)

    if payload.agg_period == AggregationPeriod.by_year:
        data = _likes_aggregation_by_year(criteria)

    return {"status": "ok", "data": data}


def _likes_aggregation_by_day(criteria):
    records = (
        db.session
        .query(
            func.date(Like.created_at).label("date"),
            func.count(Like.id).label("count"))
        .select_from(UserProfile)
        .join(Post)
        .join(Like)
        .filter(*criteria)
        .group_by(func.date(Like.created_at))
        .all()
    )
    return [{
        "day": str(r.date),
        "count": r.count
    } for r in records]


def _likes_aggregation_by_month(criteria):
    records = (
        db.session
        .query(
            func.year(Like.created_at).label("year"),
            func.month(Like.created_at).label("month"),
            func.count(Like.id).label("count"))
        .select_from(UserProfile)
        .join(Post)
        .join(Like)
        .filter(*criteria)
        .group_by(func.year(Like.created_at), func.month(Like.created_at))
        .all()
    )
    return [{
        "year": r.year,
        "month": r.month,
        "count": r.count
    } for r in records]


def _likes_aggregation_by_year(criteria):
    records = (
        db.session
        .query(
            func.year(Like.created_at).label("year"),
            func.count(Like.id).label("count"))
        .select_from(UserProfile)
        .join(Post)
        .join(Like)
        .filter(*criteria)
        .group_by(func.year(Like.created_at))
        .all()
    )
    return [{
        "year": r.year,
        "count": r.count
    } for r in records]
