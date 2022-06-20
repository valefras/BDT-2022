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
    mycursor.execute("CREATE TABLE `main_data` (`id` int NOT NULL AUTO_INCREMENT, " +
                     "`city` varchar(255) NOT NULL, " +
                     "`country` varchar(255) NOT NULL, " +
                     "`year` smallint NOT NULL, " +
                     "`cost_of_living_index` decimal(3,2) DEFAULT NULL, " +
                     "`rent_index` decimal(3,2) DEFAULT NULL, " +
                     "`groceries_index` decimal(3,2) DEFAULT NULL, " +
                     "`restaurant_price_index` decimal(3,2) DEFAULT NULL, " +
                     "`local_ppi_index` decimal(3,2) DEFAULT NULL, " +
                     "`crime_index` decimal(3,2) DEFAULT NULL, " +
                     "`safety_index` decimal(3,2) DEFAULT NULL, " +
                     "`qol_index` decimal(3,2) DEFAULT NULL, " +
                     "`ppi_index` decimal(3,2) DEFAULT NULL, " +
                     "`health_care_index` decimal(3,2) DEFAULT NULL, " +
                     "`traffic_commute_index` decimal(3,2) DEFAULT NULL, " +
                     "`pollution_index` decimal(3,2) DEFAULT NULL, " +
                     "`climate_index` decimal(3,2) DEFAULT NULL, " +
                     "`gross_rental_yield_centre` decimal(3,2) DEFAULT NULL, " +
                     "`gross_rental_yield_out` decimal(3,2) DEFAULT NULL, " +
                     "`price_to_rent_centre` decimal(3,2) DEFAULT NULL, " +
                     "`price_to_rent_out` decimal(3,2) DEFAULT NULL, " +
                     "`affordability_index` decimal(3,2) DEFAULT NULL, " +
                     "PRIMARY KEY (`id`))" +
                     "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;")
    close_connection(mycursor, mydb)

create_db()
create_tables()