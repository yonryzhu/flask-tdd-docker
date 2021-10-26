from src import db
from src.api.users.models import User


def get_all_users() -> list[User]:
    return User.query.all()


def get_user_by_id(user_id: int) -> User:
    return User.query.filter_by(id=user_id).first()


def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()


def add_user(username: str, email: str) -> User:
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user: User, username: str, email: str) -> User:
    user.username = username
    user.email = email
    db.session.commit()
    return user


def delete_user(user: User) -> User:
    db.session.delete(user)
    db.session.commit()
    return user
