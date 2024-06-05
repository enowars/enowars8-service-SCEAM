import os
import sqlite3
import datetime
import time

CLEANUP_INTERVAL = datetime.timedelta(minutes=15)
# CLEANUP_INTERVAL = datetime.timedelta(seconds=10)

db_path = os.path.dirname(__file__)
db_path = os.path.join(db_path, 'instance')
uploads_path = os.path.join(db_path, 'uploads')
db_path = os.path.join(db_path, 'database.db')


class db_cleanup():
    def __init__(self) -> None:
        self.time = datetime.datetime.now()
        self.cut_off = self.time - CLEANUP_INTERVAL
        # Check if database exists
        if not os.path.exists(db_path):
            return
        self.db = sqlite3.connect(db_path)

        self.cleanup()
        self.db.commit()
        self.db.close()

    def cleanup(self):
        self.cleanup_users()
        self.cleanup_uploads()

    def cleanup_files(self, names_list):
        full_path = os.path.join(uploads_path, 'full')
        lossy_path = os.path.join(uploads_path, 'lossy')

        for i in names_list:
            try:
                os.remove(os.path.join(full_path, i))
                os.remove(os.path.join(lossy_path, i))
            except:
                print("file not found")

    def cleanup_uploads(self):
        all_uploads = self.db.execute('SELECT * FROM enoft').fetchall()
        all_uploads = list(map(lambda x: list(x), all_uploads))
        for i in all_uploads:
            i[4] = datetime.datetime.strptime(i[4], '%Y-%m-%d %H:%M:%S')

        to_be_deleted = list(
            filter(lambda x: x[4] < self.cut_off or x[-2] in self.deleted_owners, all_uploads))
        names = list(map(lambda x: x[1], to_be_deleted))
        self.cleanup_files(names)

        to_be_deleted = list(map(lambda x: x[0], to_be_deleted))

        for i in to_be_deleted:
            self.db.execute('DELETE from enoft WHERE id=?', (i,))

    def cleanup_users(self):
        all_users = self.db.execute('SELECT * FROM user').fetchall()
        all_users = list(map(lambda x: list(x), all_users))
        for i in all_users:
            i[6] = datetime.datetime.strptime(i[6], '%Y-%m-%d %H:%M:%S')
        to_be_deleted = list(
            filter(lambda x: x[6] < self.cut_off, all_users))
        to_be_deleted = list(map(lambda x: x[1], to_be_deleted))
        self.deleted_owners = to_be_deleted
        for i in to_be_deleted:
            self.db.execute('DELETE from user WHERE email=?', (i,))


if __name__ == '__main__':
    seconds_to_sleep = 60*5
    # seconds_to_sleep = 10
    while True:
        print(f"Running cleanup every {seconds_to_sleep} seconds")
        db_cleanup()
        time.sleep(seconds_to_sleep)
