"""
Загрузка из файла sbis_employ.json в таблицу organisation
"""
from db.db_connector import execute, fetchone
from pathlib import Path
from typing import Generator, Any, List
from itertools import chain
import ijson

import settings


def table_exist(table):
    return bool(
        fetchone(
            """SELECT TRUE FROM sbis.pg_catalog.pg_tables WHERE schemaname = 'public' AND tablename = %s;""",
            table,
        )
    )


def recreate_data():
    if table_exist("organisation"):
        execute("DROP TABLE organisation")
    execute(
        """
    CREATE TABLE organisation (
    "id" integer NOT NULL PRIMARY KEY ,
    "ParentId" integer REFERENCES organisation (id),
    "Name" text NOT NULL,
    "Type" integer NOT NULL);
    """
    )
    load_data_in_db()


def chunk_iter(*, size_chunk: int, gen: Generator[Any, None, None]) -> List[Any]:
    """Считывает из генератора и возвращает списки в 10 элементов"""
    chunk = []
    while True:
        # Создаем новый enumerate и возвращаем из gen size_chunk или менее элементов передавая их в список chunk
        for n, item in enumerate(gen, start=1):
            chunk.append(item)
            if not n % size_chunk:
                break
        # Если в chunk что-то попало, возвращаем список вызывающему коду и чистим chunk для нового захода
        if chunk:
            yield chunk
            chunk.clear()
        else:
            # Если в chunk пуст, значит gen тоже пуст, выходим из цикла и из функции
            break


def get_json_rows() -> Generator[dict, None, None]:
    """Загружаем из файла json список"""
    with (Path(settings.ROOT) / "sbis_employ.json").open(mode="rb") as f:

        yield from ijson.items(f, "item")


def load_data_in_db() -> None:
    for chunk in chunk_iter(size_chunk=10, gen=get_json_rows()):
        if chunk and chunk[0]:
            how_match_rows = len(chunk)
            how_match_elem_in_row = len(chunk[0])
            row = "(" + ", ".join(["%s" for i in range(how_match_elem_in_row)]) + ")"
            rows = ",\n".join([row for i in range(how_match_rows)])

            execute(
                f"INSERT INTO organisation VALUES {rows} ",
                [*chain(*[x.values() for x in chunk])],
            )


if __name__ == "__main__":
    recreate_data()
