from flask import Flask, session
import json
import pymysql
import os
import datetime
from argon2 import PasswordHasher

app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(minutes=60) # Persists user's session for an hour
#app.secret_key = "mysupersecretkey"
wsgi_app = app.wsgi_app

development = True
UPLOAD_DIR = ""
settings = None

if development:    # Config for local machine
    file = open("settings.json")
    settings = json.load(file)
    file.close()

    UPLOAD_DIR = os.getcwd() + "/static/uploads"
else:    # Config for pythonanywhere
    file = open("/home/marknzl/mysite/settings_production.json")
    settings = json.load(file)
    file.close()

    UPLOAD_DIR = "/home/marknzl/mysite/static/uploads"

app.secret_key = settings["appSecretKey"]

# Global instance of argon2 password hasher object
hasher = PasswordHasher()

# Returns a database connection
def create_connection():
    return pymysql.connect(host=settings["host"],
                           user=settings["user"],
                           password=settings["password"],
                           db=settings["db"],
                           charset=settings["charset"],
                           cursorclass=pymysql.cursors.DictCursor)

def user_logged_in():
    if "user" in session:
        return True
    else:
        return False

def file_check():
    connection = create_connection()

    with connection.cursor() as cursor:
        sql = "SELECT location FROM tblfiles"
        cursor.execute(sql)

        file_locations = list(cursor.fetchall())
        files_to_delete = []

        # STAGE 1
        # Checks if the file record actually has a file on disk associated with it,
        # if not, then delete the record from the database

        for file_location in file_locations:
            found = False

            for file_name in os.listdir(UPLOAD_DIR):
                if file_name == file_location["location"]:
                    found = True
                    break

            if found == False:
                files_to_delete.append(file_location["location"])

        for file in files_to_delete:
            sql = "DELETE FROM tblfiles WHERE location = %s"
            vals = (file,)
            cursor.execute(sql, vals)

        # STAGE 2
        # Checks if each file on disk actually has a database record
        # associated with it, if not, then delete the file off disk

        for filename in os.listdir(UPLOAD_DIR):
            sql = "SELECT * FROM tblfiles WHERE location = %s"
            vals = (filename,)
            cursor.execute(sql, vals)
            file_record = list(cursor.fetchall())

            if len(file_record) == 0:
                os.remove(UPLOAD_DIR + "/%s" % filename)

        connection.commit()
    connection.close()

file_check()

def get_statistics():
    connection = create_connection()

    counts = {}

    with connection.cursor() as cursor:
        # For user count
        sql = "SELECT * FROM tblusers"
        cursor.execute(sql)
        users = list(cursor.fetchall())
        user_count = len(users)

        # For workshop count
        sql = "SELECT * FROM tblworkshops WHERE completed = 0"
        cursor.execute(sql)
        all_workshops = list(cursor.fetchall())
        workshop_count = len(all_workshops)

        # For subject count
        sql = "SELECT * FROM tblsubjects"
        cursor.execute(sql)
        subjects = list(cursor.fetchall())
        subject_count = len(subjects)

        # For promotion count
        sql = "SELECT * FROM tblpromotions WHERE approved = 0"
        cursor.execute(sql)
        promotions = list(cursor.fetchall())
        promotion_count = len(promotions)

        counts["user_count"] = user_count
        counts["workshop_count"] = workshop_count
        counts["subject_count"] = subject_count
        counts["promotion_count"] = promotion_count

    connection.close()

    return counts

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Views
from views.homepage import *
from views.user import *
from views.workshop import *
from views.subject import *

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
