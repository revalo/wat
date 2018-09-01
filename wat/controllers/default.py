from wat import app
from wat.utils import get_user, requires_auth
from wat.models import db
from wat.models.course import Course
from wat.models.user import User
from wat.mailinglists.ml import get_list_members

from flask import (
    redirect,
    url_for,
    render_template,
    jsonify,
    send_from_directory,
    request,
)
from sqlalchemy.sql import text

import os

PAGE_SIZE = 20


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.png", mimetype="image/png"
    )


@app.route("/")
@get_user()
def index():
    if user:
        return redirect(url_for("main"))

    return render_template("login.html")


@app.route("/<kerberos>")
@get_user()
def share_render(kerberos):
    target_user = User.query.filter(User.email == (kerberos + '@mit.edu')).first()
    courses = Course.query.filter(Course.user_id == target_user.id)

    return render_template("share.html", target_user=target_user, courses=courses)


@app.route("/classes")
@requires_auth()
def main():
    # Don't let the user view classes if they haven't
    # added theirs.

    if Course.query.filter(Course.user_id == user.id).first() is None:
        return redirect(url_for("edit"))

    current_classes = Course.query.filter(Course.user_id == user.id)

    return render_template("viewer.html", user=user, current_classes=current_classes)


def results_json(results):
    return jsonify(
        [
            {
                "kerb": x.email.split("@")[0],
                "courses": [
                    {"name": name, "code": code} for name, code in zip(x.names, x.codes)
                ],
            }
            for x in results
        ]
    )


@app.route("/api/classes/common")
@requires_auth()
def common_search():
    current_classes = Course.query.filter(Course.user_id == user.id).all()
    if len(current_classes) == 0:
        return "First fill in classes :/"

    OFFSET = request.args.get("page", default=0, type=int) * PAGE_SIZE

    class_codes = "(%s)" % (
        ",".join(tuple(["'%s'" % course.code for course in current_classes]))
    )

    class_codes = tuple([course.code for course in current_classes])

    query = """
    SELECT email, array_agg(code) AS codes, array_agg(o.name) AS names FROM course o, "user" u WHERE EXISTS (
        SELECT 1 FROM course c WHERE c.code IN :codes AND c.user_id = o.user_id
    ) AND u.id = o.user_id AND u.id != :user_id
    GROUP BY email LIMIT :limit OFFSET :offset;
    """

    results = db.engine.execute(
        text(query),
        {
            "codes": class_codes,
            "user_id": user.id,
            "limit": PAGE_SIZE,
            "offset": OFFSET,
        },
    )

    return results_json(results)


@app.route("/api/classes/search/<q>/by/<by>")
@requires_auth()
def search(q, by):
    current_classes = Course.query.filter(Course.user_id == user.id).all()
    if len(current_classes) == 0:
        return "First fill in classes :/"

    OFFSET = request.args.get("page", default=0, type=int) * PAGE_SIZE

    if by == "ml":
        query = """
        SELECT email, array_agg(code) AS codes, array_agg(o.name) AS names FROM course o, "user" u WHERE
        u.id = o.user_id AND u.id != :user_id AND split_part(u.email, '@', 1) IN :search
        GROUP BY email LIMIT :limit OFFSET :offset;
        """
        q = q.split("@")[0]
    elif by == "user":
        query = """
        SELECT email, array_agg(code) AS codes, array_agg(o.name) AS names FROM course o, "user" u WHERE
        u.id = o.user_id AND u.id != :user_id AND (split_part(u.email, '@', 1) ilike :search OR u.name ilike :search)
        GROUP BY email LIMIT :limit OFFSET :offset;
        """
    else:
        query = """
        SELECT email, array_agg(code) AS codes, array_agg(o.name) AS names FROM course o, "user" u WHERE EXISTS (
            SELECT 1 FROM course c WHERE (c.code ilike :search OR c.name ilike :search) AND c.user_id = o.user_id
        ) AND u.id = o.user_id AND u.id != :user_id
        GROUP BY email LIMIT :limit OFFSET :offset;
        """

    if by != "ml":
        results = db.engine.execute(
            text(query),
            {
                "search": "%" + q + "%",
                "user_id": user.id,
                "limit": PAGE_SIZE,
                "offset": OFFSET,
            },
        )
    else:
        members = get_list_members(q.lower())
        if len(members) == 0:
            return jsonify({"error": "Invalid list name or hidden list :/"})

        results = db.engine.execute(
            text(query),
            {
                "search": tuple(members),
                "user_id": user.id,
                "limit": PAGE_SIZE,
                "offset": OFFSET,
            },
        )

    return results_json(results)
