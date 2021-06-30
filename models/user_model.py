class User:
    def __init__(self, user_id, role, username, first_name, last_name, email):
        self.user_id = user_id
        self.role = role
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def is_admin(self):
        if self.role == "Admin":
            return True
        else:
            return False

    def is_teacher(self):
        if self.role == "Teacher":
            return True
        else:
            return False

    def is_student(self):
        if self.role == "Student":
            return True
        else:
            return False

def get_user_from_session(session):
    user = User(session["user"]["user_id"],
                session["user"]["role"],
                session["user"]["username"],
                session["user"]["first_name"],
                session["user"]["last_name"],
                session["user"]["email"])

    return user
