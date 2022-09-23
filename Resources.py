from flask import request, render_template, make_response, session
from flask_restful import Resource, reqparse
import sqlite3
import os
from werkzeug.utils import secure_filename


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
        upload_folder = os.path.join('pictures')
        uploaded_img = request.files['picture']
        img_filename = secure_filename(uploaded_img.filename)
        uploaded_img.save(os.path.join(upload_folder, img_filename))
        print(os.path.join(upload_folder, img_filename), "8888", img_filename)
        session['uploaded_img_file_path'] = os.path.join(upload_folder, img_filename)

        data = ReceiveInfo.parser.parse_args()
        print(data)
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        query = "INSERT INTO {} VALUES(NULL, ? , ?, ?, ?, ?, ?, ?, ?, ?)".format(self.TABLE_NAME)
        cursor.execute(query, (data['firstname'], data['lastname'],data['college'], data['age'], data['gender'], data['religion'], data['number'],data['fb_url'], data['job']))
        connection.commit()
        connection.close()
        return make_response(render_template("updated.html", name="{} {}".format(data['firstname'], data['lastname'], data['gender'], data['religion'], data['job'])))


class GetInfo(Resource):
    TABLE_NAME = "user"

    parser = reqparse.RequestParser()
    parser.add_argument("username",
                        type=str,
                        required=True,
                        help="Username can't be blank.")
    parser.add_argument("password",
                        type=str,
                        required=True,
                        help="Password can't left blank.")

    def get(self):
        return make_response(render_template("login.html"))

    def post(self):
        picture_folder = os.path.join('pictures')
        full_filename = os.path.join(picture_folder, "ehshanul.jpg")
        print(full_filename)
        data = GetInfo.parser.parse_args()
        print(data)
        connection = sqlite3.connect("All Information.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM user WHERE username=?", (data['username'],)).fetchone()
        if result:
            user = result
        else:
            user = None
        print(user)
        if user[1] == data['password']:
            query = "SELECT * FROM people"
            data = list(cursor.execute(query))
            info = {}
            for item in data:
                info[" ".join([item[x] for x in range(1,3)])] = [item[a] for a in range(3, len(item))]
                print(info)
        else:
            return {"message": "You have entered wrong password."}

        connection.commit()
        connection.close()
        return make_response(render_template("hudai.html", data=info, user_image=full_filename))


