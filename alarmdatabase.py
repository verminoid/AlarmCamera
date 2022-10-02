import sqlite3

def ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1

class DataBaseBot():
    """Module for connection with DB SQLite
    """    
    def __init__(self, base: str) -> None:
        """Create new connection to DB SQLite

        Args:
            base (str): file name DB in OS
        """        
        self._tg_db = sqlite3.connect(base, check_same_thread=False)
        self._tg_db.create_collation("NOCASE", ignore_case_collation)
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
        """Destroing base connection
        """        
        self._tg_db.close()

    def list_users(self, subs: bool = False) -> list:
        """Return list of ID knowed users

        Returns:
            list(int): list of ID's 
        """        
        users_id = []
        curs = self._tg_db.cursor()
        query = "SELECT user_id FROM users"
        if subs:
            query += " where subs = 1"
        curs.execute(query)
        for user in  curs.fetchall():
            users_id.append(user[0])
        curs.close()
        return users_id

    def new_user(self, user_id: int, user_name: str, name: str, subs: bool) -> None:
        """insert new user to databse

        Args:
            user_id (int): user's id from Telegramm
            user_name (str): user's name from Telegramm
            name (str): First name from Telegramm
            subs (bool): True or False autosubscribe to alarm event
        """        
        curs = self._tg_db.cursor()
        curs.execute("""INSERT INTO users
                        (user_id, user_name, name, subs)
                        VALUES(?, ?, ?, ?);
                    """, (user_id, user_name, name, subs))
        curs.close()
        self._tg_db.commit()

    def user_exists(self, user_id: int) -> bool:
        """Check of exists user in DB

        Args:
            user_id (int): user's id from telegramm

        Returns:
            bool: True if exists
        """        
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
        """Adding new camera to DB

        Args:
            cloud_id (str): cloud id xmeye
            address (str): ip address in local
            name (str): Caption Name
            user (str, optional): UserName to connect. Defaults to 'admin'.
            password (str, optional): password to connect. Defaults to ''.
        """        
        curs = self._tg_db.cursor()
        curs.execute("""INSERT INTO cams
                        (cloud_id, address, name, user, password)
                        VALUES(?, ?, ?, ?, ?);
                    """, (cloud_id, address, name, user, password))
        curs.close()
        self._tg_db.commit()
    
    def cams_list(self) -> list:
        """Return list of camera

        Returns:
            list: List camera 
        """        
        curs = self._tg_db.cursor()
        curs.execute("""SELECT * FROM cams
                        """)
        cams = curs.fetchall()
        curs.close()
        return cams

    def subs_user(self, user_id: int, subs: bool):
        curs = self._tg_db.cursor()
        curs.execute("""UPDATE users SET
                        subs = ?
                        WHERE user_id = ?;
                    """, (subs, user_id))
        curs.close()
        self._tg_db.commit()

    def cam_selection(self, name: str) -> list:
        curs = self._tg_db.cursor()
        curs.execute("""SELECT * FROM cams where name = ? COLLATE NOCASE;
                    """, (name,))
        ret = curs.fetchall()
        curs.close()
        return ret

    def cam_edit(self, cloud_id: str, address: str) -> None:
        curs = self._tg_db.cursor()
        curs.execute("""UPDATE cams SET
                        address = ?
                        WHERE cloud_id = ?;
                    """, (address, cloud_id))
        curs.close()
        self._tg_db.commit()