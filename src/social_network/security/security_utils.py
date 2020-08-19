import hashlib
import bcrypt
import base64
from uuid import uuid4
from ua_parser import user_agent_parser


def generate_refresh_token():
    return base64.b64encode(
        hashlib.sha256(uuid4().bytes).digest()
    ).decode()


def hash_password(password):
    password = password if isinstance(password, bytes) else password.encode()
    return bcrypt.hashpw(
        base64.b64encode(hashlib.sha256(password).digest()),
        bcrypt.gensalt()
    )


def compare_passwords(password, hashed_password):
    password = (
        password
        if isinstance(password, bytes)
        else password.encode()
    )
    hashed_password = (
        hashed_password
        if isinstance(hashed_password, bytes)
        else hashed_password.encode()
    )
    return bcrypt.checkpw(
        base64.b64encode(hashlib.sha256(password).digest()), 
        hashed_password
    )


def parse_user_agent(user_agent):
    ua = user_agent_parser.Parse(user_agent)
    return {
        "device": f"{ua['device']['family']} {(ua['device']['model']) or ''}",
        "os": f"{ua['os']['family']} {(ua['os']['major']) or ''}",
        "browser": f"{ua['user_agent']['family']}"
    }
    

def validate_password(password, policy):
    errors = []

    if policy["ONLY_ASCII"] and not password.isascii():
        errors.append("password must contain only ascii.")

    if policy["VARIETY_LEN"] and len(set(password)) < policy["VARIETY_LEN"]:
        errors.append(f"password is too simple.")

    if policy["MIN_LEN"] and len(password) < policy["MIN_LEN"]:
        errors.append(f"min password len - {policy['MIN_LEN']}.")

    if policy["MAX_LEN"] and len(password) > policy["MAX_LEN"]:
        errors.append(f"max password len - {policy['MIN_LEN']}.")

    if policy["CONTAINS_UPPER"] and not any(map(str.isupper, password)):
        errors.append(f"password should contain capital letters.")

    if policy["CONTAINS_LOWWER"] and not any(map(str.islower, password)):
        errors.append(f"password should contain lowwer case letters.")

    if policy["CONTAINS_NUMBERS"] and not any(map(str.isdigit, password)):
        errors.append(f"password should contain lowwer case letters.")

    if policy["CONTAINS"] and not any([(c in password) for c in policy["CONTAINS"]]):
        errors.append(f"password should contain one of {policy['CONTAINS']}.")

    if len(errors) > 0:
        msg = "\n".join(errors)
        raise ValueError(msg)
