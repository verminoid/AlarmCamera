import sqlite3

class DataBaseBot():
    def __init__(self, base: str) -> None:
        self._tg_db = sqlite3.connect(base, check_same_thread=False)
        curs = self._tg_db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS users(
                            user_id INT PRIMARY KEY,
                            user_name TEXT,
                            name TEXT,
                            subs INT);
                        """)
        curs.execute("""CREATE TABLE IF NOT EXISTS cams(
                            cloud_id TEXT PRIMARY KEY,
                            address TEXT,
                            name TEXT,
                            user TEXT,
                            password TEXT);
                        """)
        self._tg_db.commit()
        curs.close()
        
    def __del__(self):
        self._tg_db.close()

    def list_users(self) -> list:
        users_id = []
        curs = self._tg_db.cursor()
        curs.execute("""SELECT user_id FROM users
                        """)
        for user in  curs.fetchall():
            users_id.append(user[0])
        curs.close()
        return users_id

    def new_user(self, user_id: int, user_name: str, name: str, subs: bool) -> None:
        curs = self._tg_db.cursor()
        curs.execute("""INSERT INTO users
                        (user_id, user_name, name, subs)
                        VALUES(?, ?, ?, ?);
                    """, (user_id, user_name, name, subs))
        curs.close()

    def user_exists(self, user_id: int) -> bool:
        curs = self._tg_db.cursor()
        curs.execute("""SELECT * FROM users where user_id = ?;
                    """, (user_id,))
        ret = curs.fetchone()
        curs.close()
        if ret is None:
            return False
        else:
            return True

    def new_cam(self, cloud_id: str, address: str, name: str, user: str = 'admin', password: str = '') -> None:
        curs = self._tg_db.cursor()
        curs.execute("""INSERT INTO cams
                        (cloud_id, address, name, user, password)
                        VALUES(?, ?, ?, ?, ?);
                    """, (cloud_id, address, name, user, password))
        curs.close()
    
    def cams_list(self) -> list:
        curs = self._tg_db.cursor()
        curs.execute("""SELECT * FROM cams
                        """)
        cams = curs.fetchall()
        curs.close()
        return cams
