Описание решения
---
___

Решение состоит из:

    search_colleagues.py
        основной файл

    settings.py
        файл с настроками для подключения к базе данных и корневой директорией проекта

    prepare_data
        Модуль с функциями для инициализации и пересоздания таблицы organisation
    
    db
        Модуль с классом оберткой для работы с базой данных

    organisation
        Набор функций с запросами к таблице  organisation

Запуск и проверка
---
___

Для локальной проверки работоспособности можно воспользоваться Postgres запущенным в docker контейнере:
запустив из директории colleagues команду
```bash
docker-compose up -d 
```
При развертывании в директории colleagues появится папка tmp с файлом базы данных pgdata.
В контейнере уже импортирована таблица из задания, но при запуске скрипта search_colleagues\
вызывается функция recreate_data() в которой таблица с данными удаляется и создается заново\
и данные загружаются заново из файла sbis_employ.json.

Перед запуском скриптов необходимо установить зависимости указанные в requirements.txt :

```bash
pip3 install -r  requirements.txt
```

Для выборки всех сотрудников офиса по id одного из сотрудников сотрудника необходимо запустить из
консоли файл search_colleagues.py указав id сотрудника:

```bash
python3 search_colleagues.py  3
```

Чтобы отключить пересоздание данных, нужно также указать флаг --no-recreate

```bash
python3 search_colleagues.py  3 --no-recreate
```
