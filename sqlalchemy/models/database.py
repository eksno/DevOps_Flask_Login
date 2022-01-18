"""SQLAlchemy ORM models."""

import sqlalchemy as sa
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
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    email = sa.Column(sa.UnicodeText(), nullable=False, index=True, unique=True)
    username = sa.Column("username", sa.UnicodeText(), nullable=False)
    password = sa.relationship("Password", backref="user")
    user_token = sa.relationship("UserToken", backref="user")


class Password(Base):
    __tablename__ = 'passwords'

    user = sa.relationship("User", backref="password")
    password = sa.Column(sa.UnicodeText(), nullable=False)


class UserToken(Base):
    __tablename__ = 'user_tokens'

    user = sa.relationship("User", backref="user_tokens")
    user_token = sa.Column(sa.UnicodeText(), nullable=False)
