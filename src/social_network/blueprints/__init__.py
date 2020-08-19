from .auth import auth_blueprint
from .posts import posts_blueprint
from .users import users_blueprint


__all__ = ["auth_blueprint", "posts_blueprint", "users_blueprint"]
