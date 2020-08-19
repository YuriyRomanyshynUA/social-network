from datetime import datetime
from flask import request
from flask import Blueprint
from sqlalchemy import func
from sqlalchemy.orm import joinedload
#
from social_network import db
from social_network.errors import ApplicationError
from social_network.security import jwt_auth
from social_network.domain_models import Post
from social_network.domain_models import Like
from social_network.domain_models import UserProfile

from .payload_models import PostCreatePayload
from .payload_models import PostLookupPayload
from .payload_models import UserPostsLookupPayload



api = Blueprint("posts", __name__)


@api.route("/api/posts/create", methods=["POST"])
@jwt_auth()
def create_post(*args, **kwargs):
    now = datetime.now()

    user = kwargs["user"]  # from jwt_auth decorator
    post_payload = PostCreatePayload(**request.get_json())

    new_post = Post(
        user_profile = user.profile,
        title = post_payload.title,
        content = post_payload.content,
        created_at = now
    )

    db.session.add(new_post)
    db.session.commit()

    return {
        "status": "ok",
        "value": new_post.id
    }


@api.route("/api/post/<int:post_id>", methods=["GET"])
@jwt_auth()
def get_post(post_id, *args, **kwargs):

    post, likes_count = (
        db.session.query(Post, func.count(Like.id))
        .outerjoin(Like)
        .filter(Post.id == 2)
        .filter(Post.deleted_at.is_(None))
        .filter(Like.deleted_at.is_(None))
        .options(joinedload(Post.user_profile))
        .first()
    )

    if post is None:
        return {"status": "ok", "data": []}

    data = {
        "user": {
            "id": post.user_profile.user_id,
            "full_name": post.user_profile.full_name,
            "city": post.user_profile.city,
            "country": post.user_profile.country,
            "sex": post.user_profile.sex,
            "birthday": post.user_profile.birthday
        },
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published_at": int(post.created_at.timestamp() * 1000),
            "likes_count": likes_count
        }
    }

    return {
        "status": "ok",
        "data": [data]
    }

@api.route("/api/posts/user/<int:user_id>", methods=["GET"])
@jwt_auth()
def get_user_posts(user_id, *args, **kwargs):
    lookup_payload = UserPostsLookupPayload(
        user_id=user_id,
        **request.args
    )
    offset = (lookup_payload.page - 1) * lookup_payload.limit

    total_posts_count = (
        db.session.query(Post)
        .filter(Post.user_id == lookup_payload.user_id)
        .filter(Post.deleted_at.is_(None))
        .count()
    )

    total_pages_count = (
        int(total_posts_count / lookup_payload.limit)
        + int((total_posts_count % lookup_payload.limit) != 0)
    )

    if lookup_payload.page > total_pages_count:
        return {
            "status": "ok",
            "data": [],
            "total_posts_count": total_posts_count,
            "total_pages_count": total_pages_count,
            "has_more": False,
            "query": lookup_payload.dict()
        }

    posts = (
        db.session.query(Post, func.count(Like.id))
        .outerjoin(Like)
        .filter(Post.user_id == lookup_payload.user_id)
        .filter(Post.deleted_at.is_(None))
        .filter(Like.deleted_at.is_(None))
        .group_by(Post.id)
        .limit(lookup_payload.limit)
        .offset(offset)
        .all()
    )

    data = [{
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "published_at": int(post.created_at.timestamp() * 1000),
        "likes_count": likes_count
    } for (post, likes_count) in posts]

    return {
        "status": "ok",
        "data": data,
        "total_posts_count": total_posts_count,
        "total_pages_count": total_pages_count,
        "has_more": False,
        "query": lookup_payload.dict()
    }



@api.route("/api/posts/lookup", methods=["GET"])
@jwt_auth()
def posts_lookup(*args, **kwargs):

    lookup_payload = PostLookupPayload(**request.args)

    criteria = [
        Post.deleted_at.is_(None),
        UserProfile.deleted_at.is_(None)
    ]

    if lookup_payload.user_full_name:
        criteria.append(
            UserProfile.full_name.like(f"%{lookup_payload.user_full_name}%")
        )

    if lookup_payload.title:
        criteria.append(
            Post.title.like(f"%{lookup_payload.title}%")
        )

    if lookup_payload.content:
        criteria.append(
            Post.content.like(f"%{lookup_payload.content}%")
        )

    total_posts_count = (
        db.session.query(Post)
        .join(UserProfile)
        .filter(*criteria)
        .count()
    )

    offset = (lookup_payload.page - 1) * lookup_payload.limit
    total_pages_count = (
        int(total_posts_count / lookup_payload.limit)
        + int((total_posts_count % lookup_payload.limit) != 0)
    )

    if lookup_payload.page > total_pages_count:
        return {
            "status": "ok",
            "data": [],
            "total_posts_count": total_posts_count,
            "total_pages_count": total_pages_count,
            "has_more": False,
            "query": lookup_payload.dict()
        }

    criteria.append(Like.deleted_at.is_(None))

    posts = (
        db.session.query(Post, func.count(Like.id))
        .join(UserProfile)
        .outerjoin(Like)
        .filter(*criteria)
        .group_by(Post.id)
        .limit(lookup_payload.limit)
        .offset(offset)
        .all()
    )

    data = [{
        "user": {
            "id": post.user_profile.user_id,
            "full_name": post.user_profile.full_name,
            "city": post.user_profile.city,
            "country": post.user_profile.country,
            "sex": post.user_profile.sex,
            "birthday": post.user_profile.birthday
        },
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published_at": int(post.created_at.timestamp() * 1000),
            "likes_count": likes_count
        }
    } for (post, likes_count) in posts]

    return {
        "status": "ok",
        "data": data,
        "total_posts_count": total_posts_count,
        "total_pages_count": total_pages_count,
        "has_more": lookup_payload.page < total_pages_count,
        "query": lookup_payload.dict()
    }
    

@api.route("/api/post/like", methods=["POST"])
@jwt_auth()
def like_post(*args, **kwargs):
    now = datetime.now()
    user = kwargs["user"]  # from jwt_auth decorator
    post_id = request.args["post_id"]

    if not post_id.isdigit():
        raise ApplicationError("Invalid post id.", code=400)

    # === post exists ====

    post, likes_count = (
        db.session.query(Post, func.count(Like.id))
        .outerjoin(Like)
        .filter(Post.id == post_id)
        .filter(Post.deleted_at.is_(None))
        .filter(Like.deleted_at.is_(None))
        .first()
    )

    if post is None:
        raise ApplicationError("post does not exist", code=404)

    # === is it the user post === 
    
    if post.user_id == user.profile.id:
        return {"status": "ok", "value": likes_count}

    # === did user like it prev ===

    user_already_liked = (
        db.session.query(Like)
        .filter(Like.post_id == post.id)
        .filter(Like.user_id == user.id)
        .filter(Like.deleted_at.is_(None))
        .exists()
    )

    if user_already_liked:
        return {"status": "ok", "value": 0}

    # === add like to post ===

    post.likes.append(Like(
        post_id=post_id,
        user_id=user.profile.id,
        created_at=now
    ))

    db.session.add(post)
    db.session.commit()

    return {
        "status": "ok",
        "value": likes_count + 1
    }


@api.route("/api/post/unlike", methods=["POST"])
@jwt_auth()
def unlike_post(*args, **kwargs):
    now = datetime.now()
    user = kwargs["user"]  # from jwt_auth decorator
    post_id = request.args["post_id"]

    if not post_id.isdigit():
        raise ApplicationError("Invalid post id.", code=400)

    post_likes_count = (
        db.session.query(Like)
        .filter(Like.post_id == post_id)
        .filter(Like.deleted_at.is_(None))
        .count()
    )

    # === did user like this post in the past == 

    like = (
        db.session.query(Like)
        .filter(Like.user_id == user.profile.id)
        .filter(Like.post_id == post_id)
        .filter(Like.deleted_at.is_(None))
        .first()
    )

    if like is None:
        return {"status": "ok", "value": post_likes_count}

    # === delete like ===

    like.updated_at = now
    like.deleted_at = now
    db.session.commit()

    return {"status": "ok", "value": post_likes_count - 1}
