from flask import render_template, make_response, request, session
from flask_restful import Resource
from flask_login import login_required, current_user
import requests
import os

from models.students import Students
from database import db


class Home(Resource):
    TABLE_NAME = 'people'

    def get(self):
        if current_user.is_authenticated:
            student_usernames, teacher_username = Students.find_all_username()
        else:
            student_usernames = None
            teacher_username = None
        return make_response(render_template("home.html",
                                             student_usernames=student_usernames, teacher_username=teacher_username))


class ReceiveInfo(Resource):
    TABLE_NAME = 'people'

    def get(self):
        print("get")
        if current_user.is_authenticated:
            student_usernames, teacher_username = Students.find_all_username()
        else:
            student_usernames = None
            teacher_username = None
        return make_response(render_template("form.html",
                                             student_usernames=student_usernames, teacher_username=teacher_username))

    def post(self):
        data = dict(request.form.items())
        # initializing put method
        if data['work'] == 'Update':
            info = Students.find_by_username(data['username'], data['job'])
            student_usernames, teacher_username = Students.find_all_username()
            return make_response(render_template("update_form.html", data=info, student_usernames=student_usernames))

        elif data['work'] == 'init update':
            if request.files['Picture']:
                data['Picture'] = True
            else:
                data['Picture'] = False

            requests.put(request.url, params=data, files={'Picture': request.files['Picture']})

            students = Students.get_all_students()
            student_usernames, teacher_username = Students.find_all_username()

            return make_response(
                render_template("showinfo.html", students=students, teacher_username=teacher_username,
                                student_usernames=student_usernames,
                                message="{} {} has updated.".format(data['Firstname'], data['Lastname'])))

        # initializing delete method
        elif data["work"] == 'Delete':
            name = Students.find_name_by_username(data['username'])
            requests.delete(request.url, params=data)

            all_students = Students.get_all_students()
            student_usernames, teacher_username = Students.find_all_username()
            return make_response(
                render_template("showinfo.html", students=all_students,
                                student_usernames=student_usernames, teacher_username=teacher_username,
                                message="{} has deleted.".format(name)))

        else:
            if current_user.is_authenticated:
                teacher_username = current_user.username
            else:
                teacher_username = data['teacher_username']
            username = Students.generate_username(data['firstname'])
            new_student = Students(firstname=data['firstname'], lastname=data['lastname'], college=data['college'],
                                   age=data['age'], gender=data.get('gender'), religion=data.get('religion'),
                                   contact_number=data['number'], fb_url=data['fb_url'], job=data['job'],
                                   image_path=None, username=username,
                                   teacher_username=teacher_username)

            new_student.save_to_db()

            # saving picture in pictures folder and path in database
            image_path = Students.find_picture(username)
            uploaded_img = request.files['picture']
            uploaded_img.save(image_path)
            # session['uploaded_img_file_path'] = image_path

            student = Students.query.filter_by(Username=username).first()
            student.Image_Path = image_path
            student.save_to_db()
            if current_user.is_authenticated:
                student_usernames, teacher_username = Students.find_all_username()
            else:
                student_usernames = None
            return make_response(render_template("uploaded.html", name="{} {}".format(data['firstname'],
                                                                                      data['lastname'],
                                                                                      student_usernames
                                                                                      =student_usernames)))

    def put(self):
        data = dict(request.args)

        image_path = Students.find_picture(data['Username'])
        if data['Picture'] == "True":
            uploaded_img = request.files['Picture']
            uploaded_img.save(image_path)
            session['uploaded_img_file_path'] = image_path

        data.pop('work')
        data.pop('Picture')
        Students.query.filter_by(Username=data['Username']).update(data)
        db.session.commit()

        return None

    def delete(self):
        data = dict(request.args)

        delete_student = Students.query.filter_by(Username=data['username']).first()
        delete_student.delete_from_db()

        os.remove(Students.find_picture(data['username']))
        return None


class GetInfo(Resource):

    @login_required
    def get(self):
        students = Students.get_all_students()
        # teacher, students = Students.divide(all_persons)
        student_usernames, teacher_username = Students.find_all_username()
        return make_response(
            render_template("showinfo.html", students=students,
                            student_usernames=student_usernames, teacher_username=teacher_username))


class Show(Resource):
    def get(self):
        all_students = Students.get_all_students()
        if current_user.is_authenticated:
            student_usernames, teacher_username = Students.find_all_username()
        else:
            student_usernames = None
            teacher_username = None
        return make_response(
            render_template("showinfo.html",data=all_students,
                            student_usernames=student_usernames, teacher_username=teacher_username))
