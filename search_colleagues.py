import argparse
from prepare_data.work_with_file import recreate_data
from organisation.queries import (
    get_office_id_by_staff,
    get_staff_secname_by_office_id,
    is_it_staff_id,
)

# Создаем объект парсера
parser = argparse.ArgumentParser(description="Search office colleagues")
# Добавляем параметр staff_id (передается без ключа, только как значение)
parser.add_argument(
    "staff_id",
    type=int,
    metavar="company member id",
    help="uniq id company member, must by unsigned integer",
)

# Добавляем параметр --no-recreate, работает как флаг, если указан, данные в бд не пересоздаются
parser.add_argument(
    "--no-recreate",
    dest="no_recreate",
    help="if specified, the data will not be recreated",
    action="store_true",
)

# Получаем значения аргументов переданных при запуске скрипта в командной строке
args = parser.parse_args()

# Если не указан флаг no_recreate - пересоздаем данные в БД
if not args.no_recreate:
    recreate_data()


result = None
# Если перед указанный staff_id есть в базе - вернем фамилии всех сотрудников в его офисе
if is_it_staff_id(args.staff_id):
    office_id = get_office_id_by_staff(staff_id=args.staff_id)
    result = get_staff_secname_by_office_id(office_id=office_id)
else:
    # Иначе, сообщим об ошибке
    print(
        f"Company member with staff_id {args.staff_id} is not exist, please check your input."
    )

if result:
    print(" ".join(result))
