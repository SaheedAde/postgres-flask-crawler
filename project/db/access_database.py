from typing import Dict

import psycopg2

from project.db.config_database import ConfigDatabase

class AccessDataBase(ConfigDatabase):
    def __init__(self, drop: bool=False) -> None:
        self.drop = drop
        self.logger.debug('Init Class AccessDataBase')
        conn = psycopg2.connect(**self.postgres_access)
        cursor = conn.cursor()
        if self.drop:
            cursor.execute(f'DROP TABLE IF EXISTS {self.table_name};')

        query = f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
                    event_id SERIAL PRIMARY KEY NOT NULL,
                    event_title varchar(200) NOT NULL,
                    artists varchar(30)[] NOT NULL,
                    starttime date NOT NULL,
                    venue varchar(30) NOT NULL,
                    works varchar(30)[] NOT NULL,
                    image_link varchar(200) NOT NULL,
                    starting_price integer NOT NULL,
                    creation_date date DEFAULT CURRENT_TIMESTAMP)'''
        cursor.execute(query)
        cursor.close()
        conn.commit()
        self.logger.debug('CLASS AccessDataBase INITED')


    def get_events(self, indice: int=0):
        self.logger.debug('GETTING DATAS')
        conn = psycopg2.connect(**self.postgres_access)
        self.logger.debug('DB CONNECTED')
        cursor = conn.cursor()
        select_query = f"SELECT * FROM {self.table_name} ORDER BY creation_date DESC;"
        cursor.execute(select_query)
        self.logger.debug('QUERY EXECUTED')
        datas = cursor.fetchall()
        cursor.close()
        conn.commit()
        self.logger.debug('RETURNING DATAS')
        if indice:
            end = indice*3-1; start = end-2
            return datas[start:end+1]
        else: return datas


    def insert_event_in_db(self, data_rows: Dict[int, str]):
        self.logger.debug(f'INSERT INTO {self.table_name} VALUES({data_rows}) ')
        conn = psycopg2.connect(**self.postgres_access)
        cursor = conn.cursor()
        select_query = f"INSERT INTO {self.table_name}" \
                        "(event_title, artists, starttime, venue, works, image_link, starting_price)" \
                        "VALUES(%s, %s, %s, %s, %s, %s, %s);"
        insert_tuple = (data_rows['title'],
                        data_rows['artists'],
                        data_rows['datetime'],
                        data_rows['venue'],
                        data_rows['works'],
                        data_rows['image_link'],
                        data_rows['starting_price'])
        cursor.execute(select_query, insert_tuple)
        cursor.close()
        conn.commit()
        self.logger.debug('SUCCESS')
