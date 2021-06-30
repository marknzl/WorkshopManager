from app import app, create_connection, hasher, get_statistics, user_logged_in
from flask import render_template, request, session, redirect, flash
from models.user_model import User, get_user_from_session
from utilities import *

@app.route('/user/signin', methods=['GET', 'POST'])
def sign_in():
    if user_logged_in():
        return redirect("/")

    if request.method == "POST":
        form = request.form

        handle = form["user_handle"]
        password = form["password"]

        #sql = "SELECT * FROM tblusers WHERE username = %s"
        sql = ""

        # Since users can login with either their email address
        # or username, this checks if the "@" symbol is in
        # the handle that they decide to use and then execute the 
        # appropriate SQL query.

        if "@" in handle:
            sql = "SELECT tblusers.*, tblroles.role FROM tblusers INNER JOIN tblroles ON tblroles.role_id = tblusers.role_id WHERE tblusers.email = %s"
        else:
            sql = "SELECT tblusers.*, tblroles.role FROM tblusers INNER JOIN tblroles ON tblroles.role_id = tblusers.role_id WHERE tblusers.username = %s"
            
        vals = (handle,)
        user = fetchone(sql, vals)

        if user is not None:
            correct = None

            try:
                correct = hasher.verify(user["password"], password)
            except:
                correct = False

            if correct:
                session["user"] = User(user["user_id"],
                                        user["role"],
                                        user["username"],
                                        user["first_name"],
                                        user["last_name"],
                                        user["email"]).__dict__

                # For testing purposes, ignore
                #user_obj = get_user_from_session(session)
                #print(user_obj.is_admin())
                return "success"
            else:
                return "invalid"

    return render_template("signin.html")

@app.route('/user/signout')
def logout():
    if "user" in session:
        del session["user"]

    flash("You have been logged out", "info")
    return redirect("/user/signin")

@app.route('/user/register', methods=['GET', 'POST'])
def register():
    titles = None

    if request.method == "POST":
        form = request.form

        username = form["username"]
        email = form["email"]
        first_name = form["first_name"]
        last_name = form["last_name"]
        title = int(form["title"])

        sql = "SELECT * FROM tblusers WHERE username = %s OR email = %s"
        vals = (username, email)
        user = fetchone(sql, vals)

        if user is None:
            pwd_hash = hasher.hash(form["password"])

            sql = "INSERT INTO tblusers (user_id, role_id, username, password, title_id, first_name, last_name, email) VALUES (0, %s, %s, %s, %s, %s, %s, %s)"
            vals = (3, username, pwd_hash, title, first_name, last_name, email)
            nonquery(sql, vals)

            flash("You may now login with your newly created account", "info")
            return "success"
        else:
            return "invalid"

    sql = "SELECT * FROM tbltitles"
    titles = fetchall(sql)

    return render_template("register.html", titles = titles)

# Test method for "seeding" an admin account
# if one doesn't already exist in the DB
@app.route('/user/seed')
def seed_user_account():
    sql = "SELECT * FROM tblusers WHERE role_id = 1"
    users = fetchall(sql)

    if len(users) == 0:
        sql = "INSERT INTO tblusers (role_id, username, password, first_name, last_name, email) VALUES (%s, %s, %s, %s, %s, %s)"
        pwd_hash = hasher.hash("test123")
        vals = (1, "seeduser", pwd_hash, "Seed", "User", "seeduser@pakuranga.school.nz")
        nonquery(sql, vals)
        return "Seed account created! Username: seeduser, Email: seeduser@pakuranga.school.nz, Password: test123"
    else:
        return "Admin account already exists in the database!"

# Route that provides functionality if an admin
# wants to add a user manually
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    if "user" not in session:
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if not user.is_admin():
        return render_template("403.html")

    if request.method == "POST":
        form = request.form

        username = form["username"]
        email = form["email"]
        first_name = form["first_name"]
        last_name = form["last_name"]
        role = int(form["role"])
        title_id = int(form["title"])

        # Checks if the user the admin wants to add
        # already exists in the DB based on the entered
        # email address/username.
        sql = "SELECT * FROM tblusers WHERE username = %s OR email = %s"
        vals = (username, email)
        user = fetchone(sql, vals)

        if user is None:
            pwd_hash = hasher.hash(form["password"])

            sql = "INSERT INTO tblusers (user_id, role_id, username, password, first_name, last_name, email, title_id) VALUES (0, %s, %s, %s, %s, %s, %s, %s)"
            vals = (role, username, pwd_hash, first_name, last_name, email, title_id)
            nonquery(sql, vals)

            return "success"
        else:
            return "invalid"

    titles = fetchall("SELECT * FROM tbltitles")

    return render_template("adduser.html", user = user, counts = get_statistics(), titles = titles)

@app.route('/user/delete', methods=['POST'])
def delete_user():
    if "user" not in session:
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if not user.is_admin():
        return "Unauthorized"

    form = request.form
    user_id = int(form["user_id"])

    if (user_id == 1):
        return "error"  # Hardcoded so people can't delete my account :)

    sql = "DELETE FROM tblusers WHERE user_id = %s"
    vals = (user_id,)
    nonquery(sql, vals)

    return "success"

@app.route('/user/view')
def view_users():
    if "user" not in session:
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if not user.is_admin():
        return render_template("403.html")

    users = None

    #sql = "SELECT tblusers.*, tblroles.role FROM tblusers INNER JOIN tblroles ON tblusers.role_id = tblroles.role_id  WHERE user_ID != %s"
    sql = "SELECT tblusers.*, tblroles.role FROM tblusers INNER JOIN tblroles ON tblusers.role_id = tblroles.role_id"
    #vals = (user.user_id,)
    users = fetchall(sql)


    return render_template("viewusers.html", user = user, counts = get_statistics(), users = users)

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if "user" not in session:
        return redirect("/user/signin")

    edit_restrictions = ["testadmin", "testteacher", "teststudent"]

    user = get_user_from_session(session)
    is_own = False

    if user_id == 1 and user.user_id != 1:
        return render_template("403.html")  # Hard coded so people can't edit my account,
                                            # assuming that my user ID is always = "1".

    if not (user_id == int(user.user_id) or user.is_admin()):
        return render_template("403.html")   
    if (user_id == int(user.user_id)):
        is_own = True

    if request.method == "POST":
        form = request.form

        username = form["username"]
        email = form["email"]
        first_name = form["first_name"]
        last_name = form["last_name"]
        password = form["password"]
        title_id = int(form["title"])
        pwd_hash = None

        if "password" != "":
            password = form["password"]
            pwd_hash = hasher.hash(password)

        vals = None
        sql = "SELECT tblusers.email, tblusers.username FROM tblusers"
        handle_check = fetchall(sql)

        if is_own:
            if user.email == email and user.username == username:
                pass
            else:
                # Goes through each username/email in the database,
                # if a match is found for both or either of them then
                # display an error to the user

                for handle in handle_check:
                    if user.email == email:
                        if handle["username"] == username:
                            return "same_handle"
                    elif user.username == username:
                        if handle["email"] == email:
                            return "same_handle"
                    else:
                        if handle["email"] == email or handle["username"] == username:
                            return "same_handle"
        else:
            sql = "SELECT * FROM tblusers WHERE user_id = %s"
            vals = (user_id,)
            user_to_edit = fetchone(sql, vals)

            if user_to_edit["email"] == email and user_to_edit["username"] == username:
                pass
            else:
                for handle in handle_check:
                    if user_to_edit["email"] == email:
                        if handle["username"] == username:
                            return "same_handle"
                    elif user_to_edit["username"] == username:
                        if handle["email"] == email:
                            return "same_handle"


        # If no password is entered, then we don't
        # update the user's password
        if password == "":
            sql = "UPDATE tblusers SET username = %s, email = %s, first_name = %s, last_name = %s, title_id = %s WHERE user_id = %s"
            vals = (username, email, first_name, last_name, title_id, user_id)
        else:
            sql = "UPDATE tblusers SET username = %s, email = %s, first_name = %s, last_name = %s, password = %s, title_id = %s WHERE user_id = %s"
            vals = (username, email, first_name, last_name, pwd_hash, title_id, user_id)
        nonquery(sql, vals)

        # If the user is editing their own account
        # details, then we force them to re-login so their
        # changes take affect.
        if int(user.user_id) == user_id:
            return "success_own"
        else:
            return "success"

    user_to_edit = None

    sql = "SELECT tblusers.user_id, tblusers.role_id, tblusers.username, tblusers.first_name, tblusers.last_name, tblusers.email FROM tblusers WHERE user_id  = %s"
    vals = (user_id,)
    user_to_edit = fetchone(sql, vals)

    if user_to_edit == None:
        return render_template("404.html")

    # Prohibits users editing dummy accounts based
    # on a list of restricted usernames
    for restriction in edit_restrictions:
        if user_to_edit["username"] == restriction:
            return render_template("403.html", response = "You can't edit dummy accounts! To test out user editing, please create your own account.")

    titles = fetchall("SELECT * FROM tbltitles")

    return render_template("edituser.html", user_to_edit = user_to_edit, user = user,
                          counts = get_statistics(), titles = titles)

@app.route('/user/promotionrequest', methods=['GET', 'POST'])
def promotion_request():
    if "user" not in session:
        return redirect("/user/signin")

    user = get_user_from_session(session)
    already_requested = True

    if request.method == "POST":
        form = request.form
        requested_rank = int(form["requested_rank"])

        sql = "INSERT INTO tblpromotions (user_id, desired_role, approved) VALUES (%s, %s, %s)"
        vals = (user.user_id, requested_rank, 0)
        nonquery(sql, vals)

        return "success"

    sql = "SELECT * FROM tblpromotions WHERE user_id = %s AND approved = 0"
    vals = (user.user_id,)
    promotion_record = fetchall(sql, vals)

    if len(promotion_record) == 0:
        already_requested = False

    return render_template("promotionrequest.html", user = user, counts = get_statistics(), already_requested = already_requested)

@app.route('/user/promotionrequests')
def promotion_requests():
    if "user" not in session:
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if not user.is_admin():
        return "Unauthorized"

    promotion_requests = None

    sql = "SELECT tblpromotions.*, tblusers.first_name, tblusers.last_name, tblusers.role_id as current_role, tblroles.role FROM tblpromotions INNER JOIN tblusers ON tblpromotions.user_id = tblusers.user_id INNER JOIN tblroles ON tblpromotions.desired_role = tblroles.role_id WHERE approved = 0"
    promotion_requests = fetchall(sql)

    return render_template("promotionrequests.html", user = user, counts = get_statistics, promotion_requests = promotion_requests)

@app.route('/user/promotionrequests/approve', methods=['POST'])
def approve_promotion():
    form = request.form
    promotion_id = form["promotion_id"]

    sql = "SELECT * FROM tblpromotions WHERE promotion_id = %s"
    vals = (promotion_id,)
    promotion_record = fetchone(sql, vals)

    user_id = int(promotion_record["user_id"])
    desired_role = int(promotion_record["desired_role"])

    sql = "UPDATE tblusers SET role_id = %s WHERE user_id = %s"
    vals = (desired_role, user_id)
    nonquery(sql, vals)

    sql = "UPDATE tblpromotions SET approved = 1 WHERE promotion_id = %s"
    vals = (promotion_id,)
    nonquery(sql, vals)

    return "success"

@app.route('/user/promotionrequests/deny', methods=['POST'])
def deny_promotion():
    form = request.form
    promotion_id = form["promotion_id"]

    sql = "DELETE FROM tblpromotions WHERE promotion_id = %s"
    vals = (promotion_id,)
    nonquery(sql, vals)

    return "success"