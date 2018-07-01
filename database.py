from variables import Variables


class DatabaseConnection:
    def __init__(self):
        import sqlite3
        self.conn = sqlite3.connect(Variables.database)
        self.c = self.conn.cursor()

    def exec(self, *args, **kwargs):
        self.c.execute(*args, **kwargs)

    def commit(self):
        self.conn.commit()

    def close(self, commit=False):
        if commit:
            self.commit()
        self.conn.close()


class Profile:
    @staticmethod
    def insert_profile(email, username, password_hash):
        db = DatabaseConnection()
        db.exec("INSERT INTO profiles VALUES (?, ?, ?, ?)", (email, username, password_hash, 0))
        db.close(True)
        return True

    @staticmethod
    def get(column, **selected_column):
        db = DatabaseConnection()
        for key in selected_column:
            db.exec("SELECT %s FROM profiles WHERE %s=?" % (column, key), (selected_column[key],))
            result = db.c.fetchone()
            db.close()
            return result[0] if result is not None else None

    @staticmethod
    def get_password_hash(email):
        db = DatabaseConnection()
        db.exec("SELECT password_hash FROM profiles WHERE email=?", (email,))
        result = db.c.fetchone()
        db.close()
        return result[0] if result is not None else None

    @staticmethod
    def already_exists(**columns):
        db = DatabaseConnection()
        for key in columns:
            db.exec("SELECT ? FROM profiles WHERE %s=?" % key, (key, columns[key]))
        result = db.c.fetchone()
        db.close()
        return False if result is None else True

    @staticmethod
    def debug_del():
        db = DatabaseConnection()
        db.exec("DELETE FROM profiles")
        db.close(True)


class Memes:
    @staticmethod
    def insert_meme(name, author):
        db = DatabaseConnection()
        db.exec("INSERT INTO memes VALUES (?, ?, ?, ?)", (None, name, author, None))
        db.close(True)

    @staticmethod
    def already_exists(**columns):
        db = DatabaseConnection()
        for key in columns:
            db.exec("SELECT ? FROM memes WHERE %s=?" % key, (key, columns[key]))
        result = db.c.fetchone()
        db.close()
        return False if result is None else True

    @staticmethod
    def get_from_author(author):
        db = DatabaseConnection()
        db.exec("SELECT * FROM memes WHERE author=?", (author,))
        final = []
        rows = db.c.fetchall()
        for row in rows:
            for r in row:
                final.append("%s" % r)
            print(final)
        db.close()

    @staticmethod
    def get_name_from_id(id):
        db = DatabaseConnection()
        db.exec("SELECT name FROM memes WHERE id=?", (id,))
        result = db.c.fetchone()[0]
        db.close()
        return result

    @staticmethod
    def get_latest_id():
        db = DatabaseConnection()
        db.exec("SELECT id FROM memes ORDER BY id DESC LIMIT 1")  # OFFSET 1
        recent = db.c.fetchone()[0]
        db.close()
        return recent
