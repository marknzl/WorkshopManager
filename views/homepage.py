from app import app, create_connection, user_logged_in, UPLOAD_DIR, get_statistics
from models.user_model import User, get_user_from_session
from flask import render_template, request, session, redirect, flash
from utilities import fetchall

@app.route('/')
def index():
    workshops = None

    if not user_logged_in():
        #flash("You need to be logged in to access that page!", "error")
        #return redirect("/user/signin")
        return redirect("/workshop/view/guest")

    user = get_user_from_session(session)
    user_count = 0
    workshop_count = 0
    subject_count = 0
    vals = None

    sql = ""

    # Show different workshops based on who's logged in
    # Student: Display workshops that they are enrolled in
    # Teacher: Display workshops that they are teaching
    # Admin: Display every single ongoing workshop
    if user.is_student():
        sql = "SELECT tblenrollments.*, tblworkshops.*, tblusers.*, tblsubjects.*, tbltitles.title FROM tblenrollments INNER JOIN tblworkshops ON tblworkshops.workshop_id = tblenrollments.workshop_id INNER JOIN tblusers ON tblusers.user_id = tblworkshops.user_id INNER JOIN tbltitles ON tblusers.title_id = tbltitles.title_id INNER JOIN tblsubjects ON tblsubjects.subject_id = tblworkshops.subject_id WHERE tblenrollments.user_id = %s AND tblworkshops.completed = 0"
        vals = (user.user_id,)
    elif user.is_teacher():
        sql = "SELECT tblworkshops.*, tblsubjects.* FROM tblworkshops INNER JOIN tblsubjects ON tblsubjects.subject_id = tblworkshops.subject_id WHERE user_id = %s AND completed = 0"
        vals = (user.user_id,)
    else:
        sql = "SELECT tblworkshops.*, tblsubjects.* FROM tblworkshops INNER JOIN tblsubjects ON tblsubjects.subject_id = tblworkshops.subject_id WHERE completed = 0"

    workshops = fetchall(sql, vals)


    return render_template("index.html", user = user, workshops = workshops, counts = get_statistics())