from app import app, create_connection, hasher, user_logged_in, get_statistics
from flask import render_template, request, session, redirect
from models.user_model import User, get_user_from_session
from utilities import *

@app.route('/subject/add', methods=['GET', 'POST'])
def add_subject():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return render_template("403.html")

    connection = create_connection()

    if request.method == "POST":
        form = request.form

        subject_name = form["subject_name"]
        level = form["level"]

        # Checks if the subject that the user wants
        # to add already exists in the DB
        sql = "SELECT * FROM tblsubjects WHERE subject = %s AND level = %s"
        vals = (subject_name, level)
        subject = fetchone(sql, vals)

        if not subject == None:
            return "exists"
        else:
            with connection.cursor() as cursor:
                sql = "INSERT INTO tblsubjects (subject, level) VALUES (%s, %s)"
                vals = (subject_name, level)
                cursor.execute(sql, vals)

                sql = "SELECT LAST_INSERT_ID()"
                cursor.execute(sql)
                subject_id = cursor.fetchall()[0]["LAST_INSERT_ID()"]       
            connection.commit()
            connection.close()
                
            return str(subject_id)

    return render_template("addsubject.html", user = user, counts = get_statistics())

@app.route('/subject/delete', methods=['POST'])
def delete_subject():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)

    if user.is_student():
        return "Unauthorized"

    form = request.form
    subject_id = form["subject_id"]

    sql = "DELETE FROM tblsubjects WHERE subject_id = %s"
    vals = (subject_id,)
    nonquery(sql, vals)

    return "success"

@app.route('/subject/view')
def view_subjects():
    if not user_logged_in():
        return redirect("/user/signin")

    user = get_user_from_session(session)
    subjects = None

    sql = "SELECT * FROM tblsubjects ORDER BY tblsubjects.level ASC, tblsubjects.subject ASC"
    subjects = fetchall(sql)

    return render_template("viewsubjects.html", subjects = subjects, user = user, counts = get_statistics())


