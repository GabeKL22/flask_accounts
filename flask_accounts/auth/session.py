from flask import session

def login_user(user):
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["email"] = user["email"]
    session["firstname"] = user["firstname"]
    session["lastname"] = user["lastname"]

def logout_user():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("email", None)
    session.pop("firstname", None)
    session.pop("lastname", None)
    session.pop("pending_verification_email", None)

def current_user():
    if "user_id" not in session:
        return None

    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "email": session.get("email"),
        "firstname": session.get("firstname"),
        "lastname": session.get("lastname"),
    }