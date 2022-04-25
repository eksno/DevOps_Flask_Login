"""SQLAlchemy ORM models."""

import os
import jwt
import sqlalchemy as sa
from app import app
from app.components.utils import exception_str
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

DeclerativeBase = declarative_base(metadata=meta)


class Base(DeclerativeBase):
    __abstract__ = True
    date_created = sa.Column(
        sa.DateTime, default=sa.func.current_timestamp(), nullable=False
    )
    date_modified = sa.Column(
        sa.DateTime,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, unique=True)
    email = sa.Column(sa.UnicodeText(), nullable=False, index=True, unique=True)
    username = sa.Column("username", sa.UnicodeText(), nullable=False)
    admin = sa.Column(sa.Boolean, nullable=True, default=False)

    def __repr__(self):
        return "<User %r>" % self.email

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(days=0, minutes=5),
                "iat": datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, os.environ["SECRET_KEY"], algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, os.environ["SECRET_KEY"], algorithms="HS256")
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "expired"
        except jwt.InvalidTokenError as e:
            app.logger.error("Invalid Token Error: " + exception_str(e))
            return "invalid"


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
    token = sa.Column(sa.String(120), nullable=False, unique=True)

    user = sa.orm.relationship("User", backref="user_tokens")

    def __repr__(self):
        return "<UserToken %r>" % self.token
