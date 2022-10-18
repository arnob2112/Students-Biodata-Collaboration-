from flask import render_template, make_response, request, session
from flask_restful import Resource, reqparse
import sqlite3
from profile import Student
import requests
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

    def get(self):
        print("get")
        usernames = Student.find_all_username()
        return make_response(render_template("form.html", user=usernames))

    def post(self):
        data = dict(request.form.items())

        # initializing put method
        if data['work'] == 'Update':
            info = Student.find_by_username(data['username'])
            usernames = Student.find_all_username()
            return make_response(render_template("update_form.html", data=info, user=usernames))

        elif data['work'] == 'init update':
            if request.files['picture']:
                data['picture'] = True
            else:
                data['picture'] = False

            requests.put(request.url, params=data, files={'picture': request.files['picture']})

            all_persons = Student.get_all_persons()
            teacher, students = Student.divide(all_persons)
            usernames = Student.find_all_username()

            return make_response(
                render_template("showinfo.html", teacher=teacher, students=students, data=all_persons, user=usernames,
                                message="{} {} has updated.".format(data['firstname'], data['lastname'])))

        # initializing delete method
        elif data["work"] == 'Delete':
            print(data['username'])
            name = Student.find_name_by_username(data['username'])
            print(name)
            requests.delete(request.url, params=data)

            all_persons = Student.get_all_persons()
            teacher, students = Student.divide(all_persons)
            usernames = Student.find_all_username()
            return make_response(
                render_template("showinfo.html", teacher=teacher, students=students, data=all_persons, user=usernames,
                                message="{} has deleted.".format(name)))

        else:
            username = Student.generate_username(data['firstname'])

            # saving information in database
            connection = sqlite3.connect("All Information.db")
            cursor = connection.cursor()
            query = "INSERT INTO {} VALUES(NULL, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(self.TABLE_NAME)
            cursor.execute(query, (data['firstname'], data['lastname'], data['college'], data['age'], data['gender'],
                                   data['religion'], data['number'], data['fb_url'], data['job'],
                                   None, username))
            connection.commit()
            # saving picture in pictures folder and path in database
            image_path = Student.find_picture(username)
            uploaded_img = request.files['picture']
            uploaded_img.save(image_path)
            session['uploaded_img_file_path'] = image_path

            update_query = "UPDATE {} SET Image_Path = ? WHERE Username = ?".format(self.TABLE_NAME)
            cursor.execute(update_query, (image_path, username))
            connection.commit()
            connection.close()

            usernames = Student.find_all_username()
            return make_response(render_template("uploaded.html", name="{} {}".format(data['firstname'],
                                                                                      data['lastname'],
                                                                                      user=usernames)))

    def put(self):
        data = dict(request.args)

        if data['picture'] == "True":
            image_path = Student.find_picture(data['username'])
            uploaded_img = request.files['picture']
            uploaded_img.save(image_path)
            session['uploaded_img_file_path'] = image_path

        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        update_query = "UPDATE {} SET Firstname=?, LastName=?, College=?, Age=?, Gender=?, Religion=?," \
                       "Contact_Number=?, FB_URL=?, Job=? WHERE Username=?".format(self.TABLE_NAME)
        cursor.execute(update_query, (data['firstname'], data['lastname'], data['college'], data['age'], data['gender'],
                                      data['religion'], data['number'], data['fb_url'], data['job'], data['username']))
        connection.commit()
        connection.close()
        return None

    def delete(self):
        data = dict(request.args)

        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        delete_query = "DELETE FROM {} WHERE Username=?".format(self.TABLE_NAME)
        cursor.execute(delete_query, (data['username'],))
        connection.commit()
        connection.close()

        os.remove(Student.find_picture(data['username']))
        return None


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
            all_persons = Student.get_all_persons()
        else:
            return {"message": "You have entered wrong password."}
        connection.commit()
        connection.close()

        teacher, students = Student.divide(all_persons)
        usernames = Student.find_all_username()

        return make_response(
            render_template("showinfo.html", teacher=teacher, students=students, data=all_persons, user=usernames))

    def put(self):
        print("in the put method, getinfo")
        print(request.method)


class Show(Resource):

    def get(self):
        all_persons = Student.get_all_persons()
        teacher, students = Student.divide(all_persons)
        usernames = Student.find_all_username()
        print(teacher)
        print(students)
        return make_response(
            render_template("showinfo.html", teacher=teacher, students=students, data=all_persons, user=usernames))
