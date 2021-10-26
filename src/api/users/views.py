from flask import request
from flask_restx import Namespace, Resource, fields

from src.api.users import crud
from src.api.users.models import User

users_namespace = Namespace("users")


user = users_namespace.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)


class Users(Resource):
    @users_namespace.marshal_with(user)
    def get(self, user_id: int):
        """Returns a user."""
        user = crud.get_user_by_id(user_id)
        if not user:
            users_namespace.abort(404, f"User {user_id} does not exist")
        return user, 200

    @users_namespace.expect(user, validate=True)
    def put(self, user_id: int):
        """Updates a user."""
        data = request.get_json()
        username = data["username"]
        email = data["email"]
        response = {}

        user = crud.get_user_by_id(user_id)
        if not user:
            users_namespace.abort(404, f"User {user_id} does not exist")

        if crud.get_user_by_email(email):
            response["message"] = "Sorry. That email already exists."
            return response, 400

        crud.update_user(user, username, email)
        response["message"] = f"{user.id} was updated!"
        return response, 200

    def delete(self, user_id: int):
        """Deletes a user."""
        response = {}

        user = crud.get_user_by_id(user_id)
        if user is None:
            users_namespace.abort(404, f"User {user_id} does not exist")

        crud.delete_user(user)
        response["message"] = f"{user.email} was removed!"
        return response, 200


class UsersList(Resource):
    @users_namespace.expect(user, validate=True)
    def post(self) -> tuple[dict, int]:
        """Creates a user."""
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

    @users_namespace.marshal_with(user, as_list=True)
    def get(self) -> tuple[list[User], int]:
        """Returns all users"""
        users = crud.get_all_users()
        return users, 200


users_namespace.add_resource(Users, "/<int:user_id>")
users_namespace.add_resource(UsersList, "")
