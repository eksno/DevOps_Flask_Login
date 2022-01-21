"""Flask-SQLAlchemy ORM models."""

from app import sa


class User(sa.Model):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    email = sa.Column(sa.UnicodeText(), nullable=False, index=True, unique=True)
    username = sa.Column("username", sa.UnicodeText(), nullable=False)
    password = sa.relationship("Password", backref=sa.backref("user"))
    user_token = sa.relationship("UserToken", backref=sa.backref("user"))

    def __repr__(self):
        return '<User %r>' % self.email


class Password(sa.Model):
    __tablename__ = 'passwords'

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    password = sa.Column(sa.UnicodeText(), nullable=False)

    user = sa.relationship('User', backref=sa.backref('passwords', lazy=True))

    def __repr__(self):
        return '<Password %r>' % self.password


class UserToken(sa.Model):
    __tablename__ = 'user_tokens'

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    user_token = sa.Column(sa.UnicodeText(), nullable=False)
    
    user = sa.relationship('User', backref=sa.backref('user_tokens', lazy=True))

    def __repr__(self):
        return '<UserToken %r>' % self.user_token