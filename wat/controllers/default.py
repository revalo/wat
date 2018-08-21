from wat import app
from wat.utils import get_user, requires_auth
from wat.models import db
from wat.models.course import Course
from wat.models.user import User

from flask import redirect, url_for, render_template, jsonify
from sqlalchemy.sql import text


@app.route("/")
@get_user()
def index():
    if user:
        return redirect(url_for("main"))

    return render_template("login.html")


@app.route("/classes")
@requires_auth()
def main():
    # Don't let the user view classes if they haven't
    # added theirs.

    if Course.query.filter(Course.user_id == user.id).first() is None:
        return redirect(url_for("edit"))

    current_classes = Course.query.filter(Course.user_id == user.id)

    return render_template("viewer.html", user=user, current_classes=current_classes)


@app.route("/api/classes/common")
@requires_auth()
def common_search():
    current_classes = Course.query.filter(Course.user_id == user.id).all()
    if len(current_classes) == 0:
        return "First fill in classes :/"

    class_codes = "(%s)" % (
        ",".join(tuple(["'%s'" % course.code for course in current_classes]))
    )

    class_codes = tuple([course.code for course in current_classes])

    query = """
    SELECT email, array_agg(code) AS codes, array_agg(o.name) AS names FROM course o, "user" u WHERE EXISTS (
        SELECT 1 FROM course c WHERE c.code IN :codes AND c.user_id = o.user_id
    ) AND u.id = o.user_id AND u.id != :user_id
    GROUP BY email LIMIT 50;
    """

    results = db.engine.execute(text(query), {
        'codes': class_codes,
        'user_id': user.id,
    })

    return jsonify([
        {
            'kerb': x.email.split('@')[0],
            'courses': [
                {
                    'name': name,
                    'code': code,
                }
                for name, code in zip(x.names, x.codes)
            ]
        }
        for x in results
    ])