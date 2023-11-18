import asyncio
import os

import aiomysql


class DatabaseSamples:
    CONNECTION_CONFIG = {
        "db": os.environ.get("MYSQL_DATABASE"),
        "port": 3306,
        "host": "bot-db",
        "user": os.environ.get("MYSQL_USER"),
        "password": os.environ.get("MYSQL_PASSWORD"),
        "autocommit": True,
    }

    @classmethod
    async def create_table(cls):
        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_name VARCHAR(255),
                    user_id INT);
                    """
                )
                count = await cursor.execute("""SELECT * FROM users;""")
                return count, cursor.description

    @classmethod
    async def write_read(cls):
        data = [("user1", 444), ("user2", 555)]

        async with aiomysql.connect(**cls.CONNECTION_CONFIG) as connection:
            async with connection.cursor() as cursor:
                await cursor.executemany("INSERT INTO users (user_name, user_id)" "values (%s,%s)", data)
                await cursor.execute("""SELECT * FROM users;""")
                rows = await cursor.fetchone()
        return rows


if __name__ == "__main__":

    async def check_result_coroutine():
        task_table = await asyncio.create_task(DatabaseSamples.create_table())
        task_fetch = await asyncio.create_task(DatabaseSamples.write_read())

        print(task_table)
        print(task_fetch)

    asyncio.run(check_result_coroutine())
