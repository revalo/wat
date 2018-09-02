from wat import app
from wat.utils import get_user, requires_auth
from wat.models import db
from wat.models.course import Course
from wat.models.user import User

from flask import render_template, jsonify, request

import json

with open("store/classes.json", "r") as f:
    CLASSES = json.loads(f.read())


def get_class(code):
    for k, c in CLASSES.items():
        if c["no"] == code:
            return c


@app.route("/edit")
@requires_auth()
def edit():
    current_classes = Course.query.filter(Course.user_id == user.id)

    return render_template("edit.html", current_classes=current_classes, user=user)


@app.route("/api/courses", methods=["GET", "POST"])
@requires_auth()
def courses_api():
    current_classes = Course.query.filter(Course.user_id == user.id)

    if request.method == "GET":
        return jsonify(
            [{"name": course.name, "code": course.code} for course in current_classes]
        )

    if request.method == "POST":
        final_adds = []
        final_codes = {}

        for course in request.json.get("courses", []):
            current = get_class(course["code"])
            if current:
                final_adds.append(current)
                final_codes[current["no"]] = True

        final_adds = final_adds[:10]
        already_codes = {}

        # Deletion phase.
        for course in current_classes:
            if course.code not in final_codes:
                Course.query.filter(Course.id == course.id).delete()

            already_codes[course.code] = True

        # Addition phase.
        for addition in final_adds:
            if addition["no"] not in already_codes:
                db.session.add(
                    Course(user_id=user.id, code=addition["no"], name=addition["n"])
                )

        db.session.commit()
        return "OK"
