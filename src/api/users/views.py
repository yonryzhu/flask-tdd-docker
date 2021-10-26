from flask import Blueprint, request
from flask_restx import Api, Resource, fields

from src.api.users import crud
from src.api.users.models import User

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
        user = crud.get_user_by_id(user_id)
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

        user = crud.get_user_by_id(user_id)
        if not user:
            api.abort(404, f"User {user_id} does not exist")

        if crud.get_user_by_email(email):
            response["message"] = "Sorry. That email already exists."
            return response, 400

        crud.update_user(user, username, email)
        response["message"] = f"{user.id} was updated!"
        return response, 200

    def delete(self, user_id: int):
        """Deletes a user given their user_id"""
        response = {}

        user = crud.get_user_by_id(user_id)
        if user is None:
            api.abort(404, f"User {user_id} does not exist")

        crud.delete_user(user)
        response["message"] = f"{user.email} was removed!"
        return response, 200


class UsersList(Resource):
    @api.expect(user, validate=True)
    def post(self) -> tuple[dict, int]:
        """Creates and adds a new user"""
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")

        user = crud.get_user_by_email(email)
        if user:
            response = {"message": "Sorry. That email already exists."}
            return response, 400

        user = crud.add_user(username, email)
        response = {"message": f"{email} was added!"}
        return response, 201

    @api.marshal_with(user, as_list=True)
    def get(self) -> tuple[list[User], int]:
        """Returns a list of users"""
        users = crud.get_all_users()
        return users, 200


api.add_resource(Users, "/users/<int:user_id>")
api.add_resource(UsersList, "/users")
