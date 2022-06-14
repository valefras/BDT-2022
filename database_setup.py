import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def connect():
    mydb = mysql.connector.connect(
        host=os.environ.get("HOST"),
        user=os.environ.get("USER"),
        password=os.environ.get("LOCALHOST_PASSWORD"),
        auth_plugin="mysql_native_password",
        database="bd2022",
    )
    return mydb

def close_connection(mycursor, mydb):
    mycursor.close()
    mydb.close()

def insert_city(mycursor, city):
    sql_city = "INSERT IGNORE INTO city (`city`, `country`) VALUES (%s,%s)"
    mycursor.execute(sql_city, city)
    mydb.commit()


def get_city_id(mycursor, city):
    sql_id = "SELECT id FROM city WHERE city=%s AND country=%s"
    mycursor.execute(sql_id, city)
    return mycursor.fetchall()[0]


def insert_main(mycursor, city_data):
    sql_data = "INSERT IGNORE INTO main_data (`city_id`, `year`, `cost_of_living_index`, `rent_index`) VALUES (%s,%s,%s,%s)"
    mycursor.execute(sql_data, city_data)
    mydb.commit()


def create_db():
    mydb = mysql.connector.connect(
        host=os.environ.get("HOST"),
        user=os.environ.get("USER"),
        password=os.environ.get("LOCALHOST_PASSWORD")
    )

    mycursor = mydb.cursor()

    mycursor.execute(
        "CREATE DATABASE `bd2022` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;")
    close_connection(mycursor, mydb)


def create_tables():
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE `city` (`id` int NOT NULL AUTO_INCREMENT, `city` varchar(255) NOT NULL, `country` varchar(255) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1019 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;")
    mycursor.execute("CREATE TABLE `main_data` (`id` int NOT NULL AUTO_INCREMENT, `city_id` int NOT NULL, `year` smallint NOT NULL, `cost_of_living_index` decimal(3,2) DEFAULT NULL, `rent_index` decimal(3,2) DEFAULT NULL, PRIMARY KEY (`id`), KEY `FK_city_main_data_idx` (`city_id`), CONSTRAINT `FK_city_main_data` FOREIGN KEY (`city_id`) REFERENCES `city` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;")
    close_connection(mycursor, mydb)