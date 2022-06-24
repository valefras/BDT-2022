import mysql.connector
from sqlalchemy import create_engine
import pymysql
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def connect():
    db_connection_str = f'mysql+pymysql://{os.environ.get("USER")}:{os.environ.get("LOCALHOST_PASSWORD")}@{os.environ.get("HOST")}/bd2022'
    db_connection = create_engine(db_connection_str)
    return db_connection

def connect_local():
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

def drop_city(city):
    mydb = connect_local()
    mycursor = mydb.cursor()
    sql_drop = "DELETE from main_data WHERE city = %s"
    mycursor.execute(sql_drop, city)
    mydb.commit()
    close_connection(mycursor, mydb)

'''
def insert_city(mycursor, city, mydb):
    sql_city = "INSERT IGNORE INTO city (`city`, `country`) VALUES (%s,%s)"
    mycursor.execute(sql_city, city)
    mydb.commit()


def get_city_id(mycursor, city):
    sql_id = "SELECT id FROM city WHERE city=%s AND country=%s"
    mycursor.execute(sql_id, city)
    return mycursor.fetchall()[0]


def insert_main(mycursor, city_data, mydb):
    sql_data = "INSERT IGNORE INTO main_data (`city_id`, `year`, `cost_of_living_index`, `rent_index`) VALUES (%s,%s,%s,%s)"
    mycursor.execute(sql_data, city_data)
    mydb.commit()
'''

def insert_y(df):
    mydb = connect_local()
    
    mycursor = mydb.cursor()

    cont = 0
    for row in zip(df['y'], df['country'], df['city'], df['year']):
        sql_data = "UPDATE main_data SET y = %s WHERE country = %s AND city = %s and year = %s"
        mycursor.execute(sql_data, row)
        cont += 1
        if cont > 50:
            mydb.commit()
            cont = 0
    mydb.commit()
    close_connection(mycursor, mydb)



def create_db():
    mydb = mysql.connector.connect(
        host=os.environ.get("HOST"),
        user=os.environ.get("USER"),
        password=os.environ.get("LOCALHOST_PASSWORD")
    )

    mycursor = mydb.cursor()

    mycursor.execute(
        "CREATE DATABASE IF NOT EXISTS `bd2022` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;")
    close_connection(mycursor, mydb)


def create_tables():
    mydb = connect_local()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS `main_data` (`id` int NOT NULL AUTO_INCREMENT, " +
                     "`city` varchar(255) NOT NULL, " +
                     "`country` varchar(255) NOT NULL, " +
                     "`year` smallint NOT NULL, " +
                     "`cost_of_living_index` decimal(6, 3) DEFAULT NULL, " +
                     "`rent_index` decimal(6, 3) DEFAULT NULL, " +
                     "`groceries_index` decimal(6, 3) DEFAULT NULL, " +
                     "`restaurant_price_index` decimal(6, 3) DEFAULT NULL, " +
                     "`local_ppi_index` decimal(6, 3) DEFAULT NULL, " +
                     "`crime_index` decimal(6, 3) DEFAULT NULL, " +
                     "`safety_index` decimal(6, 3) DEFAULT NULL, " +
                     "`qol_index` decimal(6, 3) DEFAULT NULL, " +
                     "`ppi_index` decimal(6, 3) DEFAULT NULL, " +
                     "`health_care_index` decimal(6, 3) DEFAULT NULL, " +
                     "`traffic_commute_index` decimal(6, 3) DEFAULT NULL, " +
                     "`pollution_index` decimal(6, 3) DEFAULT NULL, " +
                     "`climate_index` decimal(6, 3) DEFAULT NULL, " +
                     "`gross_rental_yield_centre` decimal(6, 3) DEFAULT NULL, " +
                     "`gross_rental_yield_out` decimal(6, 3) DEFAULT NULL, " +
                     "`price_to_rent_centre` decimal(6, 3) DEFAULT NULL, " +
                     "`price_to_rent_out` decimal(6, 3) DEFAULT NULL, " +
                     "`affordability_index` decimal(6, 3) DEFAULT NULL, " +
                     "`y` decimal(6, 3) DEFAULT NULL, " +
                     "PRIMARY KEY (`id`))" +
                     "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;")
    mycursor.execute("CREATE TABLE IF NOT EXISTS `predictions` (`id` int NOT NULL AUTO_INCREMENT, " +
                     "`city` varchar(255) NOT NULL, " +
                     "`country` varchar(255) NOT NULL, " +
                     "`year` smallint NOT NULL, " +
                     "`y` decimal(6, 3) DEFAULT NULL, " +
                     "PRIMARY KEY (`id`))" +
                     "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;")
    close_connection(mycursor, mydb)