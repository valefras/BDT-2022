import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import mysql.connector
import pandas
import math
from dotenv import load_dotenv
import os

load_dotenv()

mydb = mysql.connector.connect(
    host=os.environ.get("HOST"),
    user=os.environ.get("USER"),
    password=os.environ.get("LOCALHOST_PASSWORD"),
    auth_plugin="mysql_native_password",
    database="bd2022",
)

mycursor = mydb.cursor()

sql_city = "INSERT IGNORE INTO city (`city`, `country`) VALUES (%s,%s)"
sql_data = "INSERT IGNORE INTO main_data (`city_id`, `year`, `cost_of_living_index`, `rent_index`) VALUES (%s,%s,%s,%s)"
sql_id = "SELECT id FROM city WHERE city=%s AND country=%s"


if datetime.now().month <= 2:
    current_year = datetime.now().year-1
else:
    current_year = datetime.now().year


def getUrl(year):
    return "https://www.numbeo.com/cost-of-living/region_rankings.jsp?title=" + str(year)+"&region=150"


for year in range(2017, current_year):

    page = requests.get(getUrl(year))
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="t2")
    rows = results.find_all("tr")

    for entry in rows[1:]:

        toAppend = []
        datapoints = entry.find_all('td')
        city_data = entry.get_text().strip().splitlines()[1:3]
        city = entry.get_text().strip().splitlines()[0].split(', ')
        mycursor.execute(sql_city, city)
        mydb.commit()
        mycursor.execute(sql_id, city)
        city_id = mycursor.fetchall()[0]
        city_data.insert(0, city_id[0])
        city_data.insert(1, year)
        mycursor.execute(sql_data, city_data)
        mydb.commit()
mycursor.close()
mydb.close()
