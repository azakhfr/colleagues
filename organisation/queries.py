"""
Запросы к таблице organisation
"""
from typing import Optional

from db.db_connector import fetchall, fetchone
from enum import Enum


class EnRowType(int, Enum):
    """Перечисление для значений колонки Type таблицы organisation"""

    office = 1
    department = 2
    staff = 3


def is_it_staff_id(staff_id: int) -> bool:
    """
    Проверка на наличие сотрудника с id staff_id в таблице organisation
    """

    q = """SELECT "Type"
            FROM organisation
            WHERE id = %s
            """
    res = fetchone(q=q, values=[staff_id])
    if res:
        res = res[0]
        return EnRowType(res) == EnRowType.staff


def is_it_office_id(office_id: int) -> bool:
    """
    Проверка на наличие офиса с id office_id в таблице organisation
    """
    assert isinstance(office_id, int), "office_id must be integer"

    q = """SELECT "Type"
            FROM organisation
            WHERE id = %s
            """
    res = fetchone(q=q, values=[office_id])
    if res:
        res = res[0]
        return EnRowType(res) == EnRowType.office


def get_office_by_id(id_: int) -> Optional[int]:
    """Выясняет id офиса (корневого узла в графе) по id строки из таблицы organisation"""
    assert isinstance(id_, int), "id must be integer"

    # Рекурсивно вычисляем офис по заданному id
    # Блок до UNION - начальное условие
    # далее формируется и добавляется (UNION) новая таблица по правилу
    # JOIN org ON organisation."id" = org."ParentId"
    # после этого для строки родителя формируется новый запрос
    # по признаку JOIN org ON organisation."id" = org."ParentId"
    # Так происходит до тех пор, пока не происходит рекурсивный обход всей таблицы
    # условие выхода из рекурсии - пустой ответ в одной из итераций
    # строка для которой пришел пустой ответ и есть офис
    q = """
            WITH RECURSIVE org AS (
            SELECT "id", "ParentId", "Name"
            FROM organisation
            WHERE "id" = %s
        UNION
            SELECT organisation.id, organisation."ParentId", organisation."Name"
                FROM organisation
                JOIN org ON organisation."id" = org."ParentId"
        )
        SELECT id FROM org WHERE "ParentId" IS NULL;
        """
    res = fetchone(q, [id_])
    if res:
        return res[0]


def get_office_id_by_staff(staff_id: int) -> Optional[int]:
    """Выясняет id офиса по id сотрудника"""
    assert isinstance(staff_id, int), "staff_id must be integer"

    if is_it_staff_id(staff_id=staff_id):
        return get_office_by_id(staff_id)


def get_all_child_with_concrete_type_by_parent_id(*, parent_id: int, type_: int):
    """Возвращает все строки со значением type_ в "Type"
    дочерние ( чей ParentId = parent_id) относительно строки parent_id
    или её дочек на любой уровень вложенности ( ParentId -> id )"""
    assert isinstance(parent_id, int), "parent_id must be integer"
    assert isinstance(type_, int), "type_ must be integer"

    # Рекурсивно получаем всех потомков ParentId у которых "Type" = %s
    # Блок до UNION - начальное условие
    # далее формируется и добавляется (UNION) новая таблица по правилу
    # JOIN org ON organisation."ParentId" = org."id"
    # после этого для каждой строки формируется новая таблица также
    # так же по признаку JOIN org ON organisation."ParentId" = org."id"
    # Так происходит до тех пор, пока не происходит рекурсивный обход всей таблицы
    # условие выхода из рекурсии - пустой ответ в одной из итераций
    q = """
    WITH RECURSIVE org AS (
        SELECT id, "ParentId", "Name", "Type"
        FROM organisation
        WHERE "ParentId" = %s
    UNION
        SELECT organisation.id, organisation."ParentId", organisation."Name", organisation."Type"
            FROM organisation
            JOIN org ON organisation."ParentId" = org."id"
    )
    SELECT "Name" FROM org WHERE "Type" = %s ;
    """
    res = fetchall(q, [parent_id, type_])
    return res


def get_staff_secname_by_office_id(office_id: int):
    """Возвращает фамилии персонала для офиса office_id"""
    assert isinstance(office_id, int), "office_id must be integer"

    if is_it_office_id(office_id):
        return [
            staff[0]
            for staff in get_all_child_with_concrete_type_by_parent_id(
                parent_id=office_id, type_=EnRowType.staff.value
            )
        ]
