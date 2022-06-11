import requests
from bs4 import BeautifulSoup
from datetime import datetime
import database_setup as DB

to_scrape = [
    "https://www.numbeo.com/cost-of-living/region_rankings.jsp?title=",
    "https://www.numbeo.com/crime/region_rankings.jsp?title=",
    "https://www.numbeo.com/quality-of-life/region_rankings.jsp?title=",
    "https://www.numbeo.com/health-care/region_rankings.jsp?title=",
    "https://www.numbeo.com/pollution/region_rankings.jsp?title=",
    "https://www.numbeo.com/traffic/region_rankings.jsp?title=",
    "https://www.numbeo.com/property-investment/region_rankings.jsp?title="
]


def getUrl(main_link, year):
    return main_link + str(year) + "&region=150"


def scrape():
    mydb = DB.connect()
    mycursor = mydb.cursor()
    if datetime.now().month <= 2:
        current_year = datetime.now().year-1
    else:
        current_year = datetime.now().year

    to_save = {}

    for link in to_scrape:
        for year in range(2017, current_year):
            page = requests.get(getUrl(link, year))
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find(id="t2")
            rows = results.find_all("tr")

            for entry in rows[1:]:
                toAppend = []
                datapoints = entry.find_all('td')
                # da qua in poi va rivisto:
                # - insert nel primo ciclo di scraping, update negli altri (a meno che non usiamo tabelle diverse?)
                # - se la città c'è fare update, mentre se non c'è fare insert
                # - la raccolta dei campi è hardcoded per cost of living
                # in alternativa, salviamo i valori durante lo scraping e li inseriamo alla fine
                city_data = entry.get_text().strip().splitlines()[1:3]
                city = entry.get_text().strip().splitlines()[0].split(', ')
                DB.insert_city(mycursor, city)
                city_id = DB.get_city_id(mycursor, city)
                city_data.insert(0, city_id[0])
                city_data.insert(1, year)
                DB.insert_main(mycursor, city_data)

    DB.close_connection(mycursor, mydb)
