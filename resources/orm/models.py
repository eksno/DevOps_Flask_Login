"""SQLAlchemy ORM models."""

import jwt
import sqlalchemy as sa
from app import app
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base

meta = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=meta)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    email = sa.Column(sa.UnicodeText(), nullable=False, index=True, unique=True)
    username = sa.Column("username", sa.UnicodeText(), nullable=False)
    registered_on = sa.Column(sa.DateTime, nullable=False)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False) -> None:
        self.email = email
        self.password = password
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def __repr__(self):
        return "<User %r>" % self.email

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(days=0, seconds=5),
                "iat": datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, app.config.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e


class Password(Base):
    __tablename__ = "passwords"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    password = sa.Column(sa.UnicodeText(), nullable=False)

    user = sa.orm.relationship("User", backref="password")

    def __repr__(self):
        return "<Password %r>" % self.password


class UserToken(Base):
    __tablename__ = "user_tokens"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    user_token = sa.Column(sa.UnicodeText(), nullable=False)

    user = sa.orm.relationship("User", backref="user_tokens")

    def __repr__(self):
        return "<UserToken %r>" % self.user_token
