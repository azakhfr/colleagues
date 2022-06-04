"""
Модуль предоставляет функции для работы с БД
Драйвер БД pg8000.dbapi обернут в класс Database
для контроля над состоянием соединения и коммитами.
"""
from contextlib import contextmanager
from typing import Any, Tuple, Optional, Generator

from pg8000.dbapi import Cursor

from db.handler import _ConnectionDBHandler


class Database:
    """Класс для работы с базой данных"""

    con = _ConnectionDBHandler()

    def execute(self, q: str, values: list = None) -> None:
        """Метод для операций изменяющих данные"""
        if not values:
            values = []
        cur = self.con.cursor()
        cur.execute(q, values)
        self.con.commit()
        cur.close()

    def fetchone(self, q: str, values: list = None) -> Tuple[Any]:
        """Метод для получения одиночных значений"""
        if values is None:
            values = []
        if not isinstance(values, list):
            values = [values]

        cur = self.con.cursor()
        cur.execute(q, values)
        res = cur.fetchone()
        self.con.commit()
        cur.close()

        return res

    def fetchall(self, q: str, values: list = None) -> Tuple[Any, ...]:
        """Метод для получения всех значений ответа"""
        if values is None:
            values = []
        if not isinstance(values, list):
            values = [values]

        cur = self.con.cursor()
        cur.execute(q, values)
        res = cur.fetchall()
        self.con.commit()
        cur.close()

        return res

    @contextmanager
    def lazyload(
        self, query: str, chunk: int = 100
    ) -> Generator[Tuple[Any, ...], None, None]:
        """Метод для ленивой загрузки данных из базы данных.
        Служит для подготовки курсора на стороне сервера и его корректного удаления при выходе из оператора with.
        Основная работа происходит внутри генератора _gen.
                :param query: Текст запроса.
                :param chunk: число строк которое будет загружаться из базы за одну итерацию.

                :rtype:  Generator[Tuple[Any, ...]]
        """
        cursor = self.con.cursor()
        cursor.execute("START TRANSACTION")
        cursor.execute(f"DECLARE c SCROLL CURSOR FOR {query}")

        yield self._gen(cursor=cursor, chunk=chunk)
        self.con.commit()
        cursor.close()

    @staticmethod
    def _gen(*, cursor: Cursor, chunk: int) -> Optional[Tuple[Any, ...]]:
        """
        Генератор выдающий chunk записей за итерацию.
        Возвращается из контекстного менеджера lazyload

        :param cursor: Серверный курсор через который ведется работа с БД.
        :param chunk: размер строк загружаемых из БД за раз.

        :return:
        """
        while True:
            cursor.execute(f"FETCH FORWARD {chunk} FROM c")
            x = cursor.fetchall()
            if x:
                yield from x
            else:
                break


db = Database()


def fetchall(*args, **kwargs) -> Tuple[Any, ...]:
    return db.fetchall(*args, **kwargs)


def execute(*args, **kwargs) -> None:
    db.execute(*args, **kwargs)


def fetchone(*args, **kwargs) -> Tuple[Any]:
    return db.fetchone(*args, **kwargs)


if __name__ == "__main__":

    db = Database()
    with db.lazyload("SELECT * FROM organisation") as cursor:
        for i in cursor:
            print(i)
