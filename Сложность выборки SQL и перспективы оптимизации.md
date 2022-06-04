Таблица organisation представляет собой набор ациклических ориентированных графов где:
 - В корне которых находятся строки с офисами в Санкт-Петербурге и Москве
 - Промежуточное положение занимают отделы, причем в отдел А может входить другой отдел (или несколько)
 - Листьями выступают сотрудники


Выборка всех сотрудников по указанному идентификатору сотрудника предполагает:
1) Для поиска офиса по идентификатору сотрудника\
   выполняется рекурсивный обход графа от сотрудника к его отделу\
   и далее до офиса в котором находится отдел (поиск корня)

2) Для посика всех сотрудников офиса - рекурсивный обход графа от офиса к сотрудникам принадлежащим к отделам офиса (поиск листьев)

___
Запрос **(1)** 
```postgresql
EXPLAIN (ANALYZE)  WITH RECURSIVE org AS (
            SELECT "id", "ParentId", "Name"
            FROM organisation
            WHERE "id" = 3
        UNION
            SELECT organisation.id, organisation."ParentId", organisation."Name"
                FROM organisation
                JOIN org ON organisation."id" = org."ParentId"
        )
        SELECT id FROM org WHERE "ParentId" IS NULL;
```
Выполняется за 816 миллисекунд и поскольку у потомка может быть только один родитель время выполнения для 
этого запроса при росте таблицы будет расти в зависимости от числа промежуточных узлов на пути ик корню.
Т.е. время выполнения запроса зависит от места узла с заданным (в запросе ниже"id" = 3) в иерархии.
Если структура иерархии не будет меняться - время запроса не будет меняться. 

```postgresql
+---------------------------------------------------------------------------------------------------------------------------------------------+
|QUERY PLAN                                                                                                                                   |
+---------------------------------------------------------------------------------------------------------------------------------------------+
|CTE Scan on org  (cost=269.82..271.84 rows=1 width=4) (actual time=0.177..0.465 rows=1 loops=1)                                              |
|  Filter: ("ParentId" IS NULL)                                                                                                               |
|  Rows Removed by Filter: 2                                                                                                                  |
|  CTE org                                                                                                                                    |
|    ->  Recursive Union  (cost=0.15..269.82 rows=101 width=40) (actual time=0.036..0.456 rows=3 loops=1)                                     |
|          ->  Index Scan using organisation_pkey on organisation  (cost=0.15..8.17 rows=1 width=40) (actual time=0.032..0.034 rows=1 loops=1)|
|                Index Cond: (id = 3)                                                                                                         |
|          ->  Hash Join  (cost=0.33..25.96 rows=10 width=40) (actual time=0.055..0.057 rows=1 loops=3)                                       |
|                Hash Cond: (organisation_1.id = org_1."ParentId")                                                                            |
|                ->  Seq Scan on organisation organisation_1  (cost=0.00..21.30 rows=1130 width=40) (actual time=0.008..0.009 rows=19 loops=2)|
|                ->  Hash  (cost=0.20..0.20 rows=10 width=4) (actual time=0.009..0.009 rows=1 loops=3)                                        |
|                      Buckets: 1024  Batches: 1  Memory Usage: 8kB                                                                           |
|                      ->  WorkTable Scan on org org_1  (cost=0.00..0.20 rows=10 width=4) (actual time=0.001..0.001 rows=1 loops=3)           |
|Planning time: 0.226 ms                                                                                                                      |
|Execution time: 0.590 ms                                                                                                                     |
+---------------------------------------------------------------------------------------------------------------------------------------------+
```
---
Запрос **(2)** 
```postgresql

EXPLAIN (ANALYZE)  WITH RECURSIVE org AS (
        SELECT id, "ParentId", "Name", "Type"
        FROM organisation
        WHERE "ParentId" = 1
    UNION
        SELECT organisation.id, organisation."ParentId", organisation."Name", organisation."Type"
            FROM organisation
            JOIN org ON organisation."ParentId" = org."id"
    )
    SELECT "Name" FROM org WHERE "Type" = 3 ;
```
Представляет обход графа в глубину и время его выполнение растет при добавлении каждого нового узла в графе 
(нового сотрудника или отдела). 
Для ускорения этого запроса можно:
1) Хранить индекс поиска офиса для каждого узла в графе.
2) Хранить путь к вершине в виде списка в дополнительном поле таблицы organisation, и при поиске вглубь\
   заменить обход графа проверкой на вхождение "id" корня в список для каждого узла в таблице
   Такой вариант также можно проиндексировать.


```postgresql
+---------------------------------------------------------------------------------------------------------------------------------------------+
|QUERY PLAN                                                                                                                                   |
+---------------------------------------------------------------------------------------------------------------------------------------------+
|CTE Scan on org  (cost=400.82..477.23 rows=17 width=32) (actual time=0.084..0.151 rows=3 loops=1)                                            |
|  Filter: ("Type" = 3)                                                                                                                       |
|  Rows Removed by Filter: 2                                                                                                                  |
|  CTE org                                                                                                                                    |
|    ->  Recursive Union  (cost=0.00..400.82 rows=3396 width=44) (actual time=0.032..0.146 rows=5 loops=1)                                    |
|          ->  Seq Scan on organisation  (cost=0.00..24.12 rows=6 width=44) (actual time=0.026..0.029 rows=2 loops=1)                         |
|                Filter: ("ParentId" = 1)                                                                                                     |
|                Rows Removed by Filter: 17                                                                                                   |
|          ->  Hash Join  (cost=1.95..30.88 rows=339 width=44) (actual time=0.028..0.029 rows=2 loops=2)                                      |
|                Hash Cond: (organisation_1."ParentId" = org_1.id)                                                                            |
|                ->  Seq Scan on organisation organisation_1  (cost=0.00..21.30 rows=1130 width=44) (actual time=0.001..0.002 rows=19 loops=2)|
|                ->  Hash  (cost=1.20..1.20 rows=60 width=4) (actual time=0.010..0.010 rows=2 loops=2)                                        |
|                      Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                           |
|                      ->  WorkTable Scan on org org_1  (cost=0.00..1.20 rows=60 width=4) (actual time=0.001..0.001 rows=2 loops=2)           |
|Planning time: 0.114 ms                                                                                                                      |
|Execution time: 0.285 ms                                                                                                                     |
+---------------------------------------------------------------------------------------------------------------------------------------------+

```
---


