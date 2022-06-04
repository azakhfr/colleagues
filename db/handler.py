import pg8000.dbapi
from pg8000.dbapi import Error
from settings import data_base_settings


class _ConnectionDBHandler:
    """A data descriptor that sets and returns values
    normally and prints a message logging their access.
    """

    def __init__(self):
        self.con = pg8000.dbapi.connect(
            user=data_base_settings.user,
            password=data_base_settings.password,
            host=data_base_settings.host,
            port=data_base_settings.port,
        )

    def __get__(self, obj, objtype):
        if self._connect_is_active():
            return self.con

    def __del__(self):
        self.con.close()

    def _connect_is_active(self):
        try:
            cursor = self.con.cursor()
            cursor.execute("""SELECT TRUE;""")
            res = cursor.fetchone()[0]
            cursor.close()
            return res

        except Error:
            self.__init__()
