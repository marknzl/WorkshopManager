import uuid
import os
import secrets
from app import app, create_connection, hasher, user_logged_in, UPLOAD_DIR, get_statistics
from flask import render_template, request, session, redirect, send_from_directory, flash
from models.user_model import User, get_user_from_session
from utilities import *

@app.route('/workshop/view', methods=['GET', 'POST'])
def view_workshops():
    user = None

    if not user_logged_in():
        return redirect("/user/signin")
    else:
        user = get_user_from_session(session)

    workshops = []
    available_workshops = []

    # Selects all workshops that haven't been marked as complete
    # if the user logged in is a student. There's probably a better way
    # to do this via a single query, but I haven't attempted to do that.
    if user.is_student():
        sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level, tblusers.first_name, tblusers.last_name, tbltitles.title FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id INNER JOIN tblusers ON tblworkshops.user_id = tblusers.user_id INNER JOIN tbltitles ON tblusers.title_id = tbltitles.title_id WHERE completed = 0 AND private = 0"
        workshops = fetchall(sql)

        # Loops through each workshop and checks if the max amount of students has been reached
        for workshop in workshops:
            sql = "SELECT * FROM tblenrollments WHERE workshop_id = %s"
            vals = (workshop["workshop_id"],)
            enrollments_in_workshop = fetchall(sql, vals)

            # A value of 0 means that there isn't a max # of students for the workshop,
            # thus we can add it straight away to the list of available workshops
            if int(workshop["max_students"]) == 0:
                available_workshops.append(workshop)
            else:
                # If the max student number for the workshop hasn't been
                # met, add it to the list of available workshops
                if not len(enrollments_in_workshop) >= int(workshop["max_students"]):
                    available_workshops.append(workshop)

            # If the student is already enrolled in the workshop, remove
            # it from the list of available workshops
            for enrollment in enrollments_in_workshop:
                if int(enrollment["user_id"]) == user.user_id:
                    if workshop in available_workshops:
                        available_workshops.remove(workshop)

    elif user.is_teacher():
        sql = "SELECT tblworkshops.*, tblsubjects.* FROM tblworkshops INNER JOIN tblsubjects ON tblsubjects.subject_id = tblworkshops.subject_id WHERE user_id = %s AND completed = 0"
        vals = (user.user_id,)
        available_workshops = fetchall(sql, vals)
    else:
        sql = "SELECT tblworkshops.*, tblsubjects.* FROM tblworkshops INNER JOIN tblsubjects ON tblsubjects.subject_id = tblworkshops.subject_id WHERE completed = 0"
        available_workshops = fetchall(sql)

    return render_template("viewworkshops.html", user = user, counts = get_statistics(), workshops = available_workshops)

@app.route('/workshop/view/guest')
def view_workshop_asguest():

    #if user_logged_in():
        #return render_template("403.html")

    workshops = []

    sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level, tblusers.first_name, tblusers.last_name, tbltitles.title FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id INNER JOIN tblusers ON tblworkshops.user_id = tblusers.user_id INNER JOIN tbltitles ON tblusers.title_id = tbltitles.title_id WHERE completed = 0 AND private = 0"
    workshops = fetchall(sql)

    return render_template("viewworkshopsguest.html", counts = get_statistics(), workshops = workshops)

@app.route('/workshop/view/<int:workshop_id>')
def view_workshop(workshop_id):
    if not user_logged_in():
        flash("You need to be signed in to view that page!", "error")
        return redirect("/user/signin")

    user = get_user_from_session(session)

    workshop = None
    workshop_files = None
    enrollments = None
    available_students = []

    #sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id WHERE workshop_id = %s"
    sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level, tblusers.first_name as teacher_firstname, tblusers.last_name as teacher_lastname, tbltitles.title FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id INNER JOIN tblusers ON tblworkshops.user_id = tblusers.user_id INNER JOIN tbltitles ON tblusers.title_id = tbltitles.title_id WHERE workshop_id = %s"
    vals = (workshop_id,)
    workshop = fetchone(sql, vals)

    if workshop is None:
        return render_template("404.html")

    # Get the workshop's files
    sql = "SELECT * FROM tblfiles WHERE workshop_id = %s"
    vals = (workshop_id, )
    workshop_files = fetchall(sql, vals)

    # Get the workshop's enrollments
    sql = "SELECT tblenrollments.*, tblusers.first_name, tblusers.last_name FROM tblenrollments INNER JOIN tblusers ON tblenrollments.user_id = tblusers.user_id WHERE workshop_id = %s"
    enrollments = fetchall(sql, workshop_id)

    # Gets all students that aren't enrolled in the current workshop,
    # this is used for populating the "Add student" dropdown box if a teacher/admin
    # wishes to add a student to their workshop manually.
    sql = "SELECT * FROM tblusers WHERE user_id != %s AND role_id = 3"
    vals = (user.user_id,)
    student_list = fetchall(sql, vals)

    for student in student_list:
        sql = "SELECT * FROM tblenrollments WHERE user_id = %s AND workshop_id = %s"
        s_id = student["user_id"]
        vals = (s_id, workshop_id)

        student_record = fetchall(sql, vals)

        if len(student_record) == 0:
            available_students.append(student)

    return render_template("viewworkshop.html", user = user, workshop = workshop,
                          workshop_files = workshop_files, enrollments = enrollments, available_students = available_students, counts = get_statistics())

@app.route('/workshop/view/past')
@app.route('/workshop/view/past/<int:user_id>')
def view_past_workshops(user_id=None):
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    past_workshops = None
    is_own = False

    if user_id != None:
        if not user.is_admin():
            if user.user_id != user_id:
                return render_template("403.html")

        viewing_other = True

        is_own = True

        sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id WHERE completed = 1 AND user_id = %s"
        vals = (user_id,)
        past_workshops = fetchall(sql, vals)
    else:
        sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id WHERE completed = 1"
        past_workshops = fetchall(sql)

    return render_template("pastworkshops.html", user = user, is_own = is_own,
                          past_workshops = past_workshops, counts = get_statistics())

@app.route('/workshop/add', methods=['GET', 'POST'])
def add_workshop():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    if request.method == "POST":
        form = request.form

        subject_id = form["subject"]
        workshop_name = form["workshop_name"]
        max_students = form["max_students"]
        date = form["date_time"]
        location = form["location"]
        summary = form["summary"]

        if date == '':
            return "error"

        private = 0
        code = ""

        if "private" in form:
            private = int(form["private"])
            print(private)

            code = str(secrets.token_hex(3))
            print(code)

        sql = "INSERT INTO tblworkshops (user_id, subject_id, workshop_name, max_students, date, completed, location, private, code, summary) VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s)"
        vals = (user.user_id, subject_id, workshop_name, max_students, date, location, private, code, summary)
        nonquery(sql, vals)

        return "" + code

    subjects = []

    sql = "SELECT * FROM tblsubjects ORDER BY tblsubjects.level ASC, tblsubjects.subject ASC"
    subjects = fetchall(sql)

    return render_template("addworkshop.html", user = user, subjects = subjects, counts = get_statistics())

@app.route('/workshop/complete/<int:workshop_id>', methods=['GET'])
def complete_workshop(workshop_id):
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    if user.is_teacher():
        sql = "SELECT * FROM tblworkshops WHERE workshop_id = %s"
        vals = (workshop_id,)
        workshop = fetchone(sql, vals)

        if int(workshop["user_id"]) != int(user.user_id):
            return render_template("403.html")

    sql = "UPDATE tblworkshops SET completed = 1 WHERE workshop_id = %s"
    vals = (workshop_id,)
    nonquery(sql, vals)

    return redirect("/workshop/view")

@app.route('/workshop/complete/revert/<int:workshop_id>', methods=['GET'])
def revert_workshop_completion(workshop_id):
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    sql = "SELECT * FROM tblworkshops WHERE workshop_id = %s"
    vals = (workshop_id,)
    workshop = fetchone(sql, vals)

    # Chekcs if workshop exists
    if len(workshop) < 1:
        return render_template("404.html")

    # If the user logged in is a teacher, check if
    # the host ID for the workshop that is being reverted
    # matches up with their user ID
    if user.is_teacher():
        if user.user_id != int(workshop["user_id"]):
            return render_template("403.html")

    sql = "UPDATE tblworkshops SET completed = 0 WHERE workshop_id = %s"
    vals = (workshop_id,)
    nonquery(sql, vals)

    return redirect('/workshop/view/%s' % workshop_id)

# Functionality for allowing teachers to manually add
# students to their workshop, student enrollment functionality
# is in a different route.
@app.route('/workshop/addstudent', methods=['POST'])
def manual_add_student():
    user = get_user_from_session(session)

    if user.is_student():
        return "error"

    form = request.form

    user_id = int(form["student_id"])
    workshop_id = int(form["add_student_workshop_id"])

    sql = "INSERT INTO tblenrollments (user_id, workshop_id) VALUES (%s, %s)"
    vals = (user_id, workshop_id)
    nonquery(sql, vals)

    return "success"

@app.route('/workshop/leave/<int:workshop_id>', methods=['GET'])
def leave_workshop(workshop_id):
    user = get_user_from_session(session)

    if not user_logged_in():
        return redirect("/user/signin")

    sql = "DELETE FROM tblenrollments WHERE user_id = %s AND workshop_id = %s"
    vals = (int(user.user_id), int(workshop_id))
    nonquery(sql, vals)

    return redirect("/workshop/view")

@app.route('/workshop/edit/<int:workshop_id>', methods=['GET', 'POST'])
def edit_workshop(workshop_id):
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    if request.method == "POST":
        form = request.form

        name = form["name"]
        location = form["location"]
        private = int(form["private"])
        summary = form["summary"]

        sql = "SELECT * FROM tblworkshops WHERE workshop_id = %s"
        vals = (workshop_id,)
        original_workshop = fetchall(sql, vals)
            
        original_code = original_workshop[0]["code"]
        new_code = ""
        keep_code = False

        if private == 1: # Checks if private checkbox is ticked
            if int(original_workshop[0]["private"] == 1): # If it is ticked and workshop is already private, don't modify workshop code
                new_code = original_code
                keep_code = True

            # Generate new workshop code if workshop is
            # changed from public to private
            if original_code == "":
                new_code = str(secrets.token_hex(3))
        else: # Else, revert code back to blank value, indicating that workshop is now public
            new_code = ""

        sql = "UPDATE tblworkshops SET workshop_name = %s, location = %s, private = %s, code = %s, summary = %s WHERE workshop_id = %s"
        vals = (name, location, private, new_code, summary, workshop_id)
        nonquery(sql, vals)

        if private == 1:
            if keep_code:
                return "success"
            else:
                return "success"
        else:
            return "success"

    #sql = "UPDATE tblworkshops SET subject_id = %s, workshop_name = %s, date = %s, location = %s"
    sql = "SELECT tblworkshops.*, tblsubjects.subject, tblsubjects.level FROM tblworkshops INNER JOIN tblsubjects ON tblworkshops.subject_id = tblsubjects.subject_id WHERE workshop_id = %s"
    vals = (workshop_id,)
    workshop = fetchone(sql, vals)

    if workshop == None:
        return render_template("404.html")

    if workshop["completed"] == 1:
        return render_template("403.html", response = "You can't edit a completed workshop!")

    if user.is_teacher():
        if workshop["user_id"] != user.user_id:
            return render_template("403.html")

    return render_template("editworkshop.html", user = user, counts = get_statistics(), workshop = workshop)

@app.route('/workshop/delete', methods=['POST'])
def delete_workshop():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return "Unauthorized"

    form = request.form
    workshop_id = form["workshop_id"]

    sql = "DELETE FROM tblworkshops WHERE workshop_id = %s"
    vals = (workshop_id,)
    nonquery(sql, vals)
    return "success"

# Functionality for allowing students to enroll
# themselves in a workshop of their choosing, functionality
# for allowing teachers to manually add students is
# in a different route.
@app.route('/workshop/enroll', methods=['POST'])
def enroll_for_workshop():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    workshops = []
    available_workshops = []

    if request.method == "POST":
        form = request.form

        if "private" not in form:
            workshop_id = form["workshop_id"]

            sql = "INSERT INTO tblenrollments (user_id, workshop_id) VALUES (%s, %s)"
            vals = (user.user_id, workshop_id)
            nonquery(sql, vals)

            return "success"
        else:
            workshop_code = form["workshop_code"]

            if len(workshop_code) < 6 or len(workshop_code) > 6:
                return "invalid_code"

            # Checks if workshop actually exists based on entered workshop code
            sql = "SELECT * FROM tblworkshops WHERE code = %s"
            vals = (workshop_code,)
            workshop = fetchone(sql, vals)

            if len(workshop) == 0:
                return "error"
            else:
                workshop_id = workshop["workshop_id"]

                # Checks if workshop is already at max capacity
                sql = "SELECT * FROM tblenrollments WHERE workshop_id = %s"
                vals = (workshop_id,)
                workshop_enrollments = fetchall(sql, vals)

                if len(workshop_enrollments) >= int(workshop["max_students"]):
                    return "max"

                # Checks if student is already enrolled in the workshop
                sql = "SELECT * FROM tblenrollments WHERE workshop_id = %s AND user_id = %s"
                vals = (workshop_id, user.user_id)
                enrollment_check = fetchone(sql, vals)

                if enrollment_check != None:
                    return "already enrolled"

                # If neither of the previous 2 conditions are met,
                # add the student to the workshop
                sql = "INSERT INTO tblenrollments (user_id, workshop_id) VALUES (%s, %s)"
                vals = (user.user_id, workshop_id)
                nonquery(sql, vals)

                return str(workshop_id)

@app.route('/workshop/kick', methods=['POST'])
def kick_user():
    form = request.form

    if not user_logged_in():
        #return redirect("/user/signin")
        return "error"

    user = get_user_from_session(session)

    if user.is_student():
        return "error"

    enrollment_id = form["enrollment_id"]

    sql = "DELETE FROM tblenrollments WHERE enrollment_id = %s"
    vals = (enrollment_id,)
    nonquery(sql, vals)

    return "success"

@app.route('/workshop/file/upload', methods=['POST'])
def upload_file():
    form = request.form
    json_string = ""

    if not user_logged_in():
        return "error"

    user = get_user_from_session(session)

    if user.is_student():
        return "Unauthorized"

    if 'file_upload' in request.files:
        file_upload = request.files["file_upload"]
        workshop_id = form["workshop_id"]
        connection = create_connection()

        file_name_full = file_upload.filename
        file_extension = file_upload.filename.split(".")[1] # Gets the file's extension, e.g ".jpg"
        uuid_string = str(uuid.uuid4()) + "." + file_extension # Unique file name to be stored on disk

        open(os.path.join(UPLOAD_DIR, uuid_string), "wb").write(file_upload.read()) # Writes the file to disk

        with connection.cursor() as cursor:
            sql = "INSERT INTO tblfiles (workshop_id, name, location) VALUES (%s, %s, %s)"
            vals = (workshop_id, file_name_full, uuid_string)
            cursor.execute(sql, vals)
            connection.commit()

            # Get the ID of the file which was just inserted
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            file_info = list(cursor.fetchall())

            # Store the ID of the last inserted file
            file_id = int(file_info[0]["LAST_INSERT_ID()"])

            # Get the record of the last inserted file
            sql = "SELECT * FROM tblfiles WHERE file_id = %s"
            vals = (file_id,)
            cursor.execute(sql, vals)
            file_info = list(cursor.fetchall())

            # Make JSON string to consume on the frontend
            json_string = str(file_info[0]).replace("'", '"')

        connection.close()

        return json_string
    else:
        return "error"

@app.route('/workshop/file/download/<file_location>')
def download_file(file_location):
    file_name = ""

    sql = "SELECT * FROM tblfiles WHERE location = %s"
    vals=(file_location,)
    file_info = fetchone(sql, vals)

    if file_info == None:
        connection.close()
        return render_template("404.html")

    file_name = file_info["name"]

    return send_from_directory(directory=UPLOAD_DIR, filename=file_location, as_attachment=True, attachment_filename=file_name)

@app.route('/workshop/file/delete', methods=['POST'])
def delete_file():
    form = request.form
    file_id = int(form["file_id"])

    # Query for getting the file's location on disk so that
    # the database record and the actual file on disk gets deleted.

    sql = "SELECT * FROM tblfiles WHERE file_id = %s"
    vals = (file_id,)
    file_data = fetchall(sql, vals)

    location = file_data[0]["location"]
    os.remove(os.path.join(UPLOAD_DIR, location))

    sql = "DELETE FROM tblfiles WHERE file_id = %s"
    vals = (file_id,)
    nonquery(sql, vals)

    return "success"