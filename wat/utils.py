import uuid
import jwt
import os
import datetime
import requests

from flask import redirect, request
from functools import wraps

from wat.config import *
from wat.constants import *
from wat.models.user import *


def gen_uuid():
    return str(uuid.uuid4()).replace("-", "")


def encode_token(user):
    return jwt.encode(
        {"id": user.id, "email": user.email, "iat": datetime.datetime.utcnow()},
        SECRET,
        algorithm="HS256",
    )


def decode_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])["id"]


epoch = datetime.datetime(1970, 1, 1)


def epoch_seconds(date):
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)


def requires_auth():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "jwt" in request.cookies:
                try:
                    decoded = decode_token(request.cookies["jwt"])
                except Exception as _:
                    return redirect("/login?redirect=" + request.url)
                user = User.query.filter_by(id=decoded).first()
                f.__globals__["user"] = user
                return f(*args, **kwargs)
            else:
                return redirect("/login")

        return decorated

    return decorator


def get_user():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "jwt" in request.cookies:
                try:
                    decoded = decode_token(request.cookies["jwt"])
                except Exception as _:
                    # FIXME Repeated code
                    f.__globals__["user"] = None
                    return f(*args, **kwargs)
                user = User.query.filter_by(id=decoded).first()
                f.__globals__["user"] = user
                return f(*args, **kwargs)
            else:
                f.__globals__["user"] = None
                return f(*args, **kwargs)

        return decorated

    return decorator


def val_form_keys(keys):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            for key in keys:
                if not key in request.form:
                    return "Missing: " + key, 400
                kwargs[key] = request.form[key]
            return f(*args, **kwargs)

        return decorated

    return decorator


def get_ts(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_ip(request):
    # This is to handle nginx being a proxy for this app.
    return request.headers.get("X-Forwarded-For", request.remote_addr)
