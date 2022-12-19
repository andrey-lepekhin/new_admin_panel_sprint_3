"""SQL queries used to extract data and state."""

CREATE_TABLE = """
create table if not exists states
(
    load_time  TIMESTAMP
            constraint id
            primary key
                on conflict fail,
    successful BOOL      default FALSE             not null,
    created_at TIMESTAMP default CURRENT_TIMESTAMP not null

);
"""

SELECT_LAST_SUCCESSFUL_LOAD_TIME = """
select load_time
from states
where successful = TRUE
order by created_at DESC
limit 1
"""

UPSERT_LAST_SUCCESSFUL_LOAD_TIME = """
INSERT OR
REPLACE INTO states (load_time, successful, created_at)
VALUES ('{0}', {1}, '{2}');
"""

DELETE_OLD_STATES = """
delete
from states
where created_at < DATETIME('now', '-1 year')
"""

SELECT_UPDATED_FILMWORKS = """
select fw.id                                           AS                id,
       fw.title                                        AS                title,
       fw.description                                  AS                description,
       fw.rating                                       AS                imdb_rating,
       ARRAY_AGG(DISTINCT g.name ORDER BY g.name DESC) AS                genre,
       ARRAY_AGG(DISTINCT p.id || ':::' || pfw.role || ':::' || p.full_name) persons
from content.film_work fw
         left join content.person_film_work pfw on fw.id = pfw.film_work_id
         left join content.person p on pfw.person_id = p.id
         left join content.genre_film_work gfw on fw.id = gfw.film_work_id
         left join content.genre g on gfw.genre_id = g.id
group by fw.id
having MAX(fw.updated_at) > '{0}'
    OR MAX(p.updated_at) > '{0}'
    OR MAX(gfw.updated_at) > '{0}'
    OR MAX(pfw.updated_at) > '{0}'
    OR MAX(g.updated_at) > '{0}';
        """

SELECT_ONE_FILMWORK = 'select id from content.film_work limit 1'
