from flask import Blueprint, request
from flask_restx import Api, Resource, fields

from src import db
from src.api.models import User

users_blueprint = Blueprint("users", __name__)
api = Api(users_blueprint)


user = api.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)


class Users(Resource):
    @api.marshal_with(user)
    def get(self, user_id: int):
        """Returns a user given their user_id"""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            api.abort(404, f"User {user_id} does not exist")
        return user, 200

    @api.expect(user, validate=True)
    def put(self, user_id: int):
        """Updates a user's email and name"""
        data = request.get_json()
        username = data["username"]
        email = data["email"]
        response = {}

        user = User.query.filter_by(id=user_id).first()
        if not user:
            api.abort(404, f"User {user_id} does not exist")

        if User.query.filter_by(email=email).first():
            response["message"] = "Sorry. That email already exists."
            return response, 400

        user.username = username
        user.email = email
        db.session.commit()

        response["message"] = f"{user.id} was updated!"
        return response, 200

    def delete(self, user_id: int):
        """Deletes a user given their user_id"""
        response = {}
        user = User.query.filter_by(id=user_id).first()

        if user is None:
            api.abort(404, f"User {user_id} does not exist")

        db.session.delete(user)
        db.session.commit()

        response["message"] = f"{user.email} was removed!"
        return response, 200


class UsersList(Resource):
    @api.expect(user, validate=True)
    def post(self) -> tuple[dict, int]:
        """Creates and adds a new user"""
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")

        user = User.query.filter_by(email=email).first()
        if user:
            response = {"message": "Sorry. That email already exists."}
            return response, 400

        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()

        response = {"message": f"{email} was added!"}
        return response, 201

    @api.marshal_with(user, as_list=True)
    def get(self) -> tuple[list[User], int]:
        """Returns a list of users"""
        return User.query.all(), 200


api.add_resource(Users, "/users/<int:user_id>")
api.add_resource(UsersList, "/users")
