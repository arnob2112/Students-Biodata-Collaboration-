from flask_login import current_user
from werkzeug.utils import secure_filename
import random
import os

from database import db


class Students(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Firstname = db.Column(db.String(1000))
    Lastname = db.Column(db.String(1000))
    College = db.Column(db.String(1000))
    Age = db.Column(db.Integer)
    Gender = db.Column(db.String(1000))
    Religion = db.Column(db.String(1000))
    Contact_Number = db.Column(db.String(20))
    FB_URL = db.Column(db.String(1000))
    Job = db.Column(db.String(100))
    Image_Path = db.Column(db.String(1000))
    Username = db.Column(db.String(1000), unique=True)
    Teacher_Username = db.Column(db.String(1000))

    def __init__(self, firstname, lastname, college, age, gender, religion,
                 contact_number, fb_url, job, image_path, username, teacher_username):
        self.Firstname = firstname
        self.Lastname = lastname
        self.College = college
        self.Age = age
        self.Gender = gender or 23
        self.Religion = religion or None
        self.Contact_Number = contact_number
        self.FB_URL = fb_url
        self.Job = job
        self.Image_Path = image_path
        self.Username = username
        self.Teacher_Username = teacher_username

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def find_by_username(username, job):
        result = Students.query.with_entities(Students.Firstname, Students.Lastname, Students.College, Students.Age,
                                              Students.Gender, Students.Religion, Students.Contact_Number,
                                              Students.FB_URL, Students.Job, Students.Image_Path,
                                              Students.Username)\
            .filter_by(Username=username, Teacher_Username=current_user.username, Job=job.capitalize()).first()
        print(result)
        if result:
            return list(result)  # returning all information of a student in list
        else:
            return None

    # @staticmethod
    # def find_all_firstname():
    #     firstnames = Students.query.with_entities(Students.Firstname).all()
    #     return firstnames  # returning all firstnames in list of tuples

    @staticmethod
    def find_all_username():
        students = Students.query.with_entities(Students.Firstname, Students.Lastname, Students.Username)\
            .filter_by(Teacher_Username=current_user.user, Job="Student").all()
        student_usernames = []
        for student in students:
            student_usernames.append(tuple([" ".join(student[x] for x in range(2)), student[2]]))
        try:
            teacher_username = Students.query.with_entities(Students.Username)\
                .filter_by(Teacher_Username=current_user.username, Job="Teacher").first()[0]
        except:
            teacher_username = None
        return student_usernames, teacher_username
        # returning all usernames in list of tuples -> (FirstName + LastName, Username)

    # @staticmethod
    # def find_username(firstname):
    #     username = Students.query.with_entities(Students.Username).filter_by(Firstname=firstname).first()
    #     return username  # returning username in tuple -> (username, )

    @staticmethod
    def generate_username(firstname):
        usernames = [username[0] for username in Students.query.with_entities(Students.Username).all()]
        unique_username = firstname.lower()
        while True:
            if unique_username not in usernames:
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
    def get_all_students():
        all_data = Students.query.with_entities(Students.Firstname, Students.Lastname, Students.College, Students.Age,
                                                Students.Gender, Students.Religion, Students.Contact_Number,
                                                Students.FB_URL, Students.Job, Students.Image_Path,
                                                Students.Username)\
            .filter_by(Teacher_Username=current_user.username, Job="Student").all()
        return all_data

    @staticmethod
    def find_name_by_username(username):
        result = Students.query.with_entities(Students.Firstname, Students.Lastname)\
            .filter_by(Username=username).first()
        name = " ".join(result)
        return name

    @staticmethod
    def divide(persons):
        teacher = persons[0]
        persons.pop(0)
        students = tuple(persons)
        return teacher, students
