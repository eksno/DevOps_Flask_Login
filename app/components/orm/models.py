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

DeclerativeBase = declarative_base(metadata=meta)


class Base(DeclerativeBase):
    __abstract__ = True
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, unique=True)
    date_created = sa.Column(
        sa.DateTime, default=sa.func.current_timestamp(), nullable=True
    )
    date_modified = sa.Column(
        sa.DateTime,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
        nullable=True,
    )


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, unique=True)
    email = sa.Column(sa.UnicodeText(), nullable=False, index=True, unique=True)
    username = sa.Column("username", sa.UnicodeText(), nullable=False)
    admin = sa.Column(sa.Boolean, nullable=True, default=True)

    def __repr__(self):
        return "<User %r>" % self.email

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(days=0, seconds=5),
                "iat": datetime.datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, app.config.get("SECRET_KEY"), algorithm="HS256")
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
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."


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
