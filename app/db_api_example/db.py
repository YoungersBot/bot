import logging
import sys

import mysql.connector
from mysql.connector import errorcode

from config_reader import config

# logging
logging.basicConfig(level=logging.INFO)


class Database:
    def __init__(self):
        self.db_name = config.db_name
        self.connection = None
        self.cursor = None
        self.connect_to_base()

    def connect(self):
        try:
            # new mysql connection
            self.connection = mysql.connector.connect(host="localhost",
                                                      user="root",
                                                      password="root")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.warning("Something is wrong with your user name or "
                                "password")
            else:
                logging.warning(err)
            sys.exit(1)

    def create_database(self):
        # getting the list of all the databases
        self.cursor.execute("SHOW DATABASES")
        dbs = self.cursor.fetchall()

        if (f'{self.db_name}',) not in dbs:
            try:
                self.cursor.execute(
                    f"CREATE DATABASE {self.db_name} DEFAULT CHARACTER SET 'utf8'")
                logging.info(f'Database {self.db_name} was successfully created!')
            except mysql.connector.Error as err:
                logging.warning(f"Failed creating database {self.db_name}: {err}")
                sys.exit(1)
        else:
            logging.info(f'Database {self.db_name} exists!')

    def connect_to_base(self):
        self.connect()
        self.cursor = self.connection.cursor()
        self.create_database()
        self.cursor.execute(f'USE {self.db_name}')
        self.create_tables()


    def create_tables(self):
        try:
            logging.info("Creating table subscriptions: ")
            self.cursor.execute(
                "CREATE TABLE `subscriptions` ("
                "`id` int(11) NOT NULL AUTO_INCREMENT, "
                "`user_id` int(20) NOT NULL, "
                "`username` varchar(120) NOT NULL, "
                "`subscription` bool, "
                "PRIMARY KEY (`id`)"
                ") ENGINE=InnoDB")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logging.info("subscriptions already exists.")
            else:
                logging.warning(err.msg)
        else:
            logging.info("OK")


if __name__ == '__main__':
    db = Database()
