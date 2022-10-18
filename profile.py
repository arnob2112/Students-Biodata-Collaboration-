from flask import render_template, make_response, request
from flask_restful import Resource
import sqlite3
import os
from werkzeug.utils import secure_filename
import random


class Student:
    def __init__(self, firstname):
        self.firstname = firstname

    @staticmethod
    def find_by_username(name):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "SELECT * FROM people WHERE Username=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.commit()
        connection.close()
        if row:
            return row  # returning all information of a student in list
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
        usernames = []
        for user in users:
            usernames.append(tuple([" ".join(user[x] for x in range(2)), user[2]]))
        return usernames  # returning all usernames in list of tuples -> (FirstName + LastName, Username)

    @staticmethod
    def find_username(firstname):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        username = cursor.execute("SELECT Username FROM people WHERE FirstName=?", (firstname, )).fetchone()
        connection.commit()
        connection.close()
        return username  # returning username in tuple -> (username, )

    @staticmethod
    def generate_username(firstname):
        usernames = [user[1] for user in Student.find_all_username()]
        unique_username = firstname.lower()
        while True:
            if unique_username not in usernames:
                print("username", unique_username)
                return unique_username
            else:
                random_number = random.randint(0, 100)
                unique_username = unique_username + str(random_number)

    @staticmethod
    def find_picture(username):
        upload_folder = os.path.join('static', 'pictures')
        img_filename = secure_filename(username + ".jpg")
        image_path = os.path.join(upload_folder, img_filename)
        return image_path  # creating picture path using firstname -> static\pictures\firstname.jpg

    @staticmethod
    def get_all_persons():
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "SELECT * FROM people"
        all_data = list(cursor.execute(query))
        connection.commit()
        connection.close()
        return all_data

    @staticmethod
    def find_name_by_username(username):
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "SELECT FirstName, Lastname FROM people WHERE Username=?"
        test = cursor.execute(query, (username, )).fetchone()
        print(test)
        name = " ".join(cursor.execute(query, (username, )).fetchone())
        return name

    @staticmethod
    def divide_in_there(persons):
        teacher = persons[0]
        persons.pop(0)
        students = []
        extra = len(persons) % 3
        if extra:
            for a in range(0, len(persons) - extra, 3):
                groups = []
                for b in range(3):
                    groups.append(persons[0])
                    persons.pop(0)
                students.append(tuple(groups))
            extra_group = []
            while persons:
                extra_group.append(persons[0])
                persons.pop(0)
            students.append(tuple(extra_group))

        else:
            for a in range(0, len(persons), 3):
                groups = []
                for b in range(3):
                    groups.append(persons[0])
                    persons.pop(0)
                students.append(tuple(groups))
        return teacher, students

    @staticmethod
    def divide(persons):
        teacher = persons[0]
        persons.pop(0)
        students = tuple(persons)
        return teacher, students


class Profile(Resource):
    def get(self, name):
        student = Student.find_by_username(name)
        if student:
            data = {" ".join([student[x] for x in range(1, 3)]): [student[x] for x in range(3, len(student) - 1)]}
            usernames = Student.find_all_username()
            print(data)
            print(usernames)
            return make_response(render_template("profile.html", data=data, user=usernames))
            # a single page of an student which includes all information
        else:
            return None
