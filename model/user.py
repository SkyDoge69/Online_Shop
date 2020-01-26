from database import SQLite
from errors import ApplicationError


class User(object):

    def __init__(self, email, password, name, adress, mobile_number, user_id=None):
        self.id = user_id
        self.email = email
        self.password = password
        self.name = name
        self.adress = adress
        self.mobile_number = mobile_number


    def to_dict(self):
        user_data = self.__dict__
        del user_data["password"]
        return user_data

    def save(self):
        with SQLite() as db:
            cursor = db.execute(self.__get_save_query())
            self.id = cursor.lastrowid
        return self

    @staticmethod
    def delete(user_id):
        result = None
        with SQLite() as db:
            result = db.execute("DELETE FROM user WHERE id = ?",
                    (user_id,))
        if result.rowcount == 0:
            raise ApplicationError("No value present", 404)

    @staticmethod
    def find(user_id):
        result = None
        with SQLite() as db:
            result = db.execute(
                    "SELECT email, password, name, adress, mobile_number, id FROM user WHERE id = ?",
                    (user_id,))
        user = result.fetchone()
        if user is None:
            raise ApplicationError(
                    "User with id {} not found".format(user_id), 404)
        return User(*user)

    @staticmethod
    def find_by_email(email):
        result = None
        with SQLite() as db:
            result = db.execute(
                    "SELECT email, password, name, adress, mobile_number, id FROM user WHERE email = ?",
                    (email,))
        user = result.fetchone()
        if user is None:
            raise ApplicationError(
                    "User with name {} not found".format(email), 404)
        return User(*user)

    @staticmethod
    def all():
        with SQLite() as db:
            result = db.execute(
                    "SELECT email, password, name, adress, mobile_number, id FROM user").fetchall()
            return [User(*row) for row in result]

    def __get_save_query(self):
        query = "{} INTO user {} VALUES {}"
        if self.id == None:
            args = (self.email, self.password, self.name, self.adress, self.mobile_number)
            query = query.format("INSERT", "(email, password, name, adress, mobile_number)", args)
        else:
            args = (self.id, self.email, self.password, self.name, self.adress, self.mobile_number)
            query = query.format("REPLACE", "(id, email, password, name, adress, mobile_number)", args)
        return query


