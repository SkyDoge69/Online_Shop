from database import SQLite
from errors import ApplicationError

class Ad(object):

    def __init__(self, title, content, price, release_date, is_active, buyer_id, creator_id, ad_id=None):
        self.id = ad_id
        #self.user_id = user_id
        self.title = title
        self.content = content
        self.price = price
        self.release_date = release_date
        self.is_active = is_active
        self.buyer_id = buyer_id
        self.creator_id = creator_id
	
    def to_dict(self):
        return self.__dict__

    def save(self):
        with SQLite() as db:
            cursor = db.execute(self.__get_save_query())
            self.id = cursor.lastrowid
        return self

    @staticmethod
    def delete(ad_id):
        result = None
        with SQLite() as db:
            result = db.execute("DELETE FROM ad WHERE id = ?",
                    (ad_id,))
        if result.rowcount == 0:
            raise ApplicationError("No value present", 404)

    @staticmethod
    def find(ad_id):
        result = None
        with SQLite() as db:
            result = db.execute(
                    "SELECT title, content, price, release_date, is_active, buyer_id, creator_id, id FROM ad WHERE id = ?",
                    (ad_id,))
        ad = result.fetchone()
        if ad is None:
            raise ApplicationError(
                    "Ad with id {} not found".format(ad_id), 404)
        return Ad(*ad)

    @staticmethod
    def all():
        with SQLite() as db:
            result = db.execute(
                    "SELECT title, content, price, release_date, is_active, buyer_id, creator_id, id FROM ad").fetchall()
            return [Ad(*row) for row in result]

    def __get_save_query(self):
        query = "{} INTO ad {} VALUES {}"
        if self.id == None:
            args = (self.title, self.content, self.price, self.release_date, self.is_active, self.buyer_id, self.creator_id)
            query = query.format("INSERT", "(title, content, price, release_date, is_active, buyer_id, creator_id)", args)
        else:
            args = (self.id, self.title, self.content, self.price, self.release_date, self.is_active, self.buyer_id, self.creator_id)
            query = query.format("REPLACE", "(id, title, content, price, release_date, is_active, buyer_id, creator_id)", args)
        return query



