import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import time, sleep
import random
import json

to_scrape = [
    "https://www.numbeo.com/cost-of-living",
    "https://www.numbeo.com/crime",
    "https://www.numbeo.com/quality-of-life",
    "https://www.numbeo.com/health-care",
    "https://www.numbeo.com/pollution",
    # "https://www.numbeo.com/traffic",
    "https://www.numbeo.com/property-investment"
]


def trusty_sleep(n):
    start = time()
    while (time() - start < n):
        sleep(n - (time() - start))


def getUrl(main_link, year):
    return main_link + "/region_rankings.jsp?title=" + str(year) + "&region=150"


def add_null_values(to_save, year_limit):
    print("Checking data...")
    allkeys = ["cost_of_living_index", "rent_index",
               "groceries_index", "restaurant_price_index", "local_ppi_index", "crime_index", "safety_index", "qol_index", "ppi_index", "health_care_index",
               "traffic_commute_index", "pollution_index", "climate_index", "health_care_exp_index", "pollution_exp_index", "gross_rental_yield_centre",
               "gross_rental_yield_out", "price_to_rent_centre", "price_to_rent_out", "affordability_index"]
    countries = [*to_save]
    for country in countries:
        cities = [*to_save[country]]
        for city in cities:
            for year in range(2017, year_limit):
                if year not in to_save[country][city]:
                    to_save[country][city][year] = {}
                for key in allkeys:
                    if key not in to_save[country][city][year]:
                        to_save[country][city][year][key] = None
    print("Scraping finished")
    with open("scraped_results.json", "w") as f:
        json.dump(to_save, f, indent=4)


def scrape():
    if datetime.now().month <= 2:
        current_year = datetime.now().year-1
    else:
        current_year = datetime.now().year

    to_save = {}
    cont = 0
    for link in to_scrape:
        print("Starting " + link)
        for year in range(2017, current_year + 1):
            page = requests.get(getUrl(link, year))
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find(id="t2")
            rows = results.find_all("tr")

            for entry in rows[1:]:
                datapoints = entry.find_all('td')

                city_data = entry.get_text().strip().splitlines()[1:]
                city = entry.get_text().strip().splitlines()[0].split(', ')
                if not(city[1] in to_save):
                    to_save[city[1]] = {city[0]: {year: {}}}
                elif not(city[0] in to_save[city[1]]):
                    to_save[city[1]][city[0]] = {year: {}}
                elif not(year in to_save[city[1]][city[0]]):
                    to_save[city[1]][city[0]][year] = {}

                if cont == 0:
                    db_keys = ["cost_of_living_index", "rent_index",
                               "groceries_index", "restaurant_price_index", "local_ppi_index"]
                elif cont == 1:
                    db_keys = ["crime_index", "safety_index"]
                elif cont == 2:
                    db_keys = ["qol_index", "ppi_index", "health_care_index",
                               "traffic_commute_index", "pollution_index", "climate_index"]
                elif cont == 3:
                    db_keys = ["health_care_exp_index"]
                elif cont == 4:
                    db_keys = ["pollution_exp_index"]
                else:
                    db_keys = ["gross_rental_yield_centre", "gross_rental_yield_out",
                               "price_to_rent_centre", "price_to_rent_out", "affordability_index"]

                for i in range(len(db_keys)):
                    to_save[city[1]][city[0]][year][db_keys[i]] = city_data[i]
            print(str(year) + " done")
            trusty_sleep(random.randint(2, 5))
        cont += 1
        print(link + " done")
        trusty_sleep(random.randint(2, 5))

    add_null_values(to_save, current_year + 1)
