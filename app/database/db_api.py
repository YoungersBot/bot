import asyncio
import datetime
import os

import aiomysql


class DatabaseQueries:
    CONNECTION_CONFIG = {
        "db": os.environ.get("MYSQL_DATABASE"),
        "port": 3306,
        "host": "bot-db",
        "user": os.environ.get("MYSQL_USER"),
        "password": os.environ.get("MYSQL_PASSWORD"),
        "autocommit": True,
    }

    @classmethod
    async def get_airports_coordinates(cls):
        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT name_ru, city_code, lat, lon FROM airports")
                result = await cursor.fetchall()
                await cursor.close()
                return result

    @classmethod
    async def count_airports_in_city_by_code(cls, city_code):
        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT city_code, country_id, name_ru, city_id FROM airports WHERE city_code = "
                                     f"'{city_code}'")
                result = await cursor.fetchall()
                await cursor.close()
                return result

    @classmethod
    async def find_airports_by_city_name(cls, city_name: str):
        city_name_ru = city_name.capitalize()
        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"""SELECT cities.city_name_ru, cities.city_code, countries.country_name
                                     FROM cities JOIN countries ON cities.country_id = countries.id
                                     WHERE city_name_ru = '{city_name_ru}'""")
                result = await cursor.fetchall()
                await cursor.close()
                return result

    @classmethod
    async def insert_new_user(cls, user_id, username, chat_id, city_id):
        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO users (user_id, username, chat_id, city_id)" "values (%s,"
                                     "%s,%s,%s) ON DUPLICATE KEY UPDATE city_id = %s",
                                     (user_id, username, chat_id, city_id, city_id))
                await cursor.close()


if __name__ == "__main__":

    async def check_result_coroutine():
        code = "LED"
        test_task = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(code))

        print(test_task)

    asyncio.run(check_result_coroutine())
