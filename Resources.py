from flask import render_template, make_response, request, session
from flask_restful import Resource, reqparse
import sqlite3
from profile import Student
from werkzeug.utils import secure_filename
import os


class Home(Resource):
    TABLE_NAME = 'people'

    def get(self):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        result = list(cursor.execute("SELECT FirstName, LastName, Contact_Number FROM {}".format(self.TABLE_NAME)).
                      fetchall())
        data = {}
        for item in result:
            data[" ".join([item[x] for x in range(2)])] = item[2]
        usernames = Student.find_all_username()
        return make_response(render_template("home.html", data=data, user=usernames))


class ReceiveInfo(Resource):
    TABLE_NAME = 'people'

    parser = reqparse.RequestParser()
    parser.add_argument('firstname',
                        type=str,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('lastname',
                        type=str,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('gender',
                        type=str)
    parser.add_argument('religion',
                        type=str)
    parser.add_argument('job',
                        type=str)
    parser.add_argument('college',
                        type=str)
    parser.add_argument('age',
                        type=str)
    parser.add_argument('number',
                        type=str)
    parser.add_argument('fb_url')

    def post(self):
        data = ReceiveInfo.parser.parse_args()
        # saving picture in pictures folder and path in database
        image_path = Student.find_picture(data['firstname'])
        print(image_path)

        uploaded_img = request.files['picture']
        uploaded_img.save(image_path)
        session['uploaded_img_file_path'] = image_path

        # saving information in database
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "INSERT INTO {} VALUES(NULL, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(self.TABLE_NAME)
        cursor.execute(query, (data['firstname'], data['lastname'], data['college'], data['age'], data['gender'],
                               data['religion'], data['number'], data['fb_url'], data['job'],
                               image_path, data['firstname'].lower()))
        connection.commit()
        connection.close()
        usernames = Student.find_all_username()
        return make_response(render_template("updated.html", name="{} {}".format(data['firstname'], data['lastname'],
                                                                                 data['gender'], data['religion'],
                                                                                 data['job']), user=usernames))

    def get(self):
        usernames = Student.find_all_username()
        return make_response(render_template("form.html", user=usernames))


class GetInfo(Resource):
    TABLE_NAME = "user"

    def get(self):
        return make_response(render_template("login.html"))

    def post(self):
        username = request.form['username']
        password = request.form['password']
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM user WHERE username=?", (username,)).fetchone()
        if result:
            user = result
        else:
            user = None
        if user[1] == password:
            query = "SELECT * FROM people"
            data = list(cursor.execute(query))
            info = {}
            for item in data:
                info[" ".join([item[x] for x in range(1, 3)])] = [item[a] for a in range(3, len(item)-1)]
        else:
            return {"message": "You have entered wrong password."}

        connection.commit()
        connection.close()
        usernames = Student.find_all_username()
        return make_response(render_template("showinfo.html", data=info, user=usernames))


class Show(Resource):
    def get(self):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "SELECT * FROM people"
        data = list(cursor.execute(query))
        info = {}
        for item in data:
            info[" ".join([item[x] for x in range(1, 3)])] = [item[a] for a in range(3, len(item)-1)]
        connection.commit()
        connection.close()
        usernames = Student.find_all_username()
        return make_response(render_template("showinfo.html", data=info, user=usernames))


