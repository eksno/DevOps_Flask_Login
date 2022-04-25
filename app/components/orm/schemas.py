from .models import User

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
