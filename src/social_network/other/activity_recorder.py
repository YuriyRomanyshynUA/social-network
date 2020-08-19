from datetime import datetime
from functools import wraps
from flask import request

from social_network import db
from social_network.security import parse_user_agent
from social_network.domain_models import ActivityRecord


__all__ = ["record_activity"]


def record_activity(name=None, message=None):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            user = kwargs.get("user")
            user_agent = (
                kwargs.get("user_agent")
                or parse_user_agent(request.headers.get("User-Agent", ""))
            )
            _activity_record(func, user, user_agent, name, message, *args, *kwargs)
            return func(*args, **kwargs)
        return decorator
    return wrapper



def _activity_record(func, user, user_agent, activity_name, message, *args, **kwargs):
    now = datetime.now()
    record = ActivityRecord(
        user_id=user.id if user else None,
        name=activity_name or func.__name__,
        message=message,
        os=user_agent.get("os"),
        device=user_agent.get("device"),
        browser=user_agent.get("browser"),
        ip_address=request.remote_addr,
        created_at=now
    )
    db.session.add(record)
    db.session.commit()
