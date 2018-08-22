"""Running this file sets up the PostgresSQL database
and initializes all the models.
"""

if __name__ == "__main__":
    from wat.models import db

    db.configure_mappers()
    db.create_all()
    db.session.commit()
