import sqlite3

class DataBaseBot():
    def __init__(self, base: str) -> None:
        self._tg_db = sqlite3.connect(base)
        curs = self._tg_db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS users(
                            user_id INT PRIMARY KEY,
                            user_name TEXT,
                            name TEXT
                            subs INT);
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


