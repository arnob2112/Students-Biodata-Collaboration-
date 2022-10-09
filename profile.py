from flask import render_template, make_response, request
from flask_restful import Resource
import sqlite3
import os
from werkzeug.utils import secure_filename


class Student:
    def __init__(self, firstname):
        self.firstname = firstname

    @classmethod
    def find_by_firstname(cls, name):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "SELECT * FROM people WHERE Username=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.commit()
        connection.close()
        if row:
            return list(row)  # returning all information of a student in list
        else:
            return None

    @staticmethod
    def find_all_firstname():
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        firstnames = list(cursor.execute("SELECT FirstName FROM people").fetchall())
        connection.commit()
        connection.close()
        return firstnames  # returning all firstnames in list of tuples

    @staticmethod
    def find_all_username():
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        users = list(cursor.execute("SELECT FirstName, LastName, Username FROM people ").fetchall())
        connection.commit()
        connection.close()
        usernames = {}
        for user in users:
            usernames[" ".join([user[x] for x in range(2)])] = user[2]
        return usernames  # returning all usernames in dictionary -> {FirstName + LastName: Username}

    @staticmethod
    def find_username(firstname):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        username = cursor.execute("SELECT Username FROM people WHERE FirstName=?", (firstname, )).fetchone()
        connection.commit()
        connection.close()
        return username  # returning username in tuple -> (username, )

    @staticmethod
    def find_picture(firstname):
        username = Student.find_username(firstname)[0]
        upload_folder = os.path.join('static', 'pictures')
        img_filename = secure_filename(username + ".jpg")
        image_path = os.path.join(upload_folder, img_filename)
        return image_path  # creating picture path using firstname -> static\pictures\firstname.jpg


class Profile(Resource):
    def get(self, name):
        student = Student.find_by_firstname(name)
        if student:
            data = {" ".join([student[x] for x in range(1, 3)]): [student[x] for x in range(3, len(student) - 1)]}
            usernames = Student.find_all_username()
            return make_response(render_template("profile.html", data=data, user=usernames))
            # a single page of an student which incluids all information
        else:
            return None
