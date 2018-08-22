from wat.models import db

from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType


class CourseQuery(BaseQuery, SearchQueryMixin):
    pass


class Course(db.Model):
    query_class = CourseQuery
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    code = db.Column(db.Unicode(255))
    name = db.Column(db.UnicodeText)

    search_vector = db.Column(TSVectorType("name", "code"))
