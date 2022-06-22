from urllib import response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import time, sleep
import random
import json
import numpy as np
import math
import mongodb_setup as mongo

to_scrape = [
    "https://www.numbeo.com/cost-of-living",
    "https://www.numbeo.com/crime",
    "https://www.numbeo.com/quality-of-life",
    "https://www.numbeo.com/property-investment"
]


def trusty_sleep(n):
    start = time()
    while (time() - start < n):
        sleep(n - (time() - start))


def getUrl(main_link, year):
    return main_link + "/region_rankings.jsp?title=" + str(year) + "&region=150"

def push_to_mongo(to_save):
    myconn = mongo.connect()
    mydb = mongo.createDB(myconn)
    mycoll = mongo.createColl(mydb)
    mongo.populateDB(mycoll, to_save)
    print("Data saved in database.")

def editJSON(to_save, countries):
    print("Parsing JSON...")
    result = []
    for country in countries:
        cities = [*to_save[country]]
        for city in cities:
            result.append({
                'city': city, 'country': country, 'metrics': to_save[country][city]})
    with open("new_scraped_results.txt", "w") as f:
        json.dump(result, f)
    print("JSON parsed.")
    push_to_mongo(to_save)

def calc_response(to_save, countries, current_year):
    print("Creating response variable...")
    weights = {"cost_of_living_index": -1, "rent_index": 1,
               "groceries_index": -0.5, "restaurant_price_index": -0.5, "local_ppi_index": 1, "crime_index": -1, "safety_index": 1, "qol_index": 1, "ppi_index": 1, "health_care_index": 1,
               "traffic_commute_index": -0.5, "pollution_index": -1, "climate_index": 0.5, "gross_rental_yield_centre": 1,
               "gross_rental_yield_out": 1, "price_to_rent_centre": -1, "price_to_rent_out": -1, "affordability_index": 1}
    for country in countries:
        cities = [*to_save[country]]
        for city in cities:
            for year in range(2017, current_year + 1):
                resp = 0
                for key in [*weights]:
                    resp += (to_save[country][city][str(year)][key] * weights[key])
                to_save[country][city][str(year)]["y"] = round(resp, 2)
    print("Response variable created.")
    with open("scraped_results.json", "w") as f:
        json.dump(to_save, f, indent=4)
    editJSON(to_save, countries)


def generate_missing(to_save, current_year, countries):
    print("Generating missing values...")
    allkeys = {"cost_of_living_index": 0, "rent_index": 1,
               "groceries_index": 2, "restaurant_price_index": 3, "local_ppi_index": 4, "crime_index": 5, "safety_index": 6, "qol_index": 7, "ppi_index": 8, "health_care_index": 9,
               "traffic_commute_index": 10, "pollution_index": 11, "climate_index": 12, "gross_rental_yield_centre": 13,
               "gross_rental_yield_out": 14, "price_to_rent_centre": 15, "price_to_rent_out": 16, "affordability_index": 17}
    
    rand_dists = {}
    skipped = set()
    means_general = [[0, 0] for col in range(len(allkeys))]
    st_devs_general = [[0, 0] for col in range(len(allkeys))]
    for country in countries:
        means = [[0, 0] for col in range(len(allkeys))]
        cities = [*to_save[country]]
        for city in cities:
            for year in range(2017, current_year + 1):
                for key in [*allkeys]:
                    if to_save[country][city][str(year)][key] != None:
                        means[allkeys[key]][0] += to_save[country][city][str(year)][key]
                        means[allkeys[key]][1] += 1
                        means_general[allkeys[key]][0] += to_save[country][city][str(year)][key]
                        means_general[allkeys[key]][1] += 1
        
        no_vals = False
        for key in [*allkeys]:
            if not no_vals:
                try:
                    means[allkeys[key]][0] = means[allkeys[key]][0] / means[allkeys[key]][1]
                except:
                    no_vals = True
                    skipped.add(country)
                    break
            else:
                break
        
        if not no_vals:
            st_devs = [0 for col in range(len(allkeys))]
            for city in cities:
                for year in range(2017, current_year + 1):
                    for key in [*allkeys]:
                        if to_save[country][city][str(year)][key] != None:
                            st_devs[allkeys[key]] += math.pow((to_save[country][city][str(year)][key] - means[allkeys[key]][0]), 2)
                            st_devs_general[allkeys[key]][0] += math.pow((to_save[country][city][str(year)][key] - means[allkeys[key]][0]), 2)
                            st_devs_general[allkeys[key]][1] += 1
            for key in [*allkeys]:
                if(means[allkeys[key]][1] == 1):
                    st_devs[allkeys[key]] = 0
                else:
                    st_devs[allkeys[key]] = math.sqrt(st_devs[allkeys[key]] / (means[allkeys[key]][1] - 1))

            rand_dists[country] = [[] for col in range(len(allkeys))]
            for key in [*allkeys]:
                rand_dists[country][allkeys[key]] = np.random.normal(means[allkeys[key]][0], st_devs[allkeys[key]], 15)

    for key in [*allkeys]:
        means_general[allkeys[key]][0] = means_general[allkeys[key]][0] / means_general[allkeys[key]][1]

    for key in [*allkeys]:
        st_devs_general[allkeys[key]][0] = st_devs_general[allkeys[key]][0] / st_devs_general[allkeys[key]][1]
        if(means_general[allkeys[key]][1] == 1):
            st_devs_general[allkeys[key]][0] = 0
        else:
            st_devs_general[allkeys[key]][0] = math.sqrt(st_devs_general[allkeys[key]][0] / (means_general[allkeys[key]][1] - 1))

    for c in skipped:
        del to_save[c]
    countries = [*to_save]
    for country in countries:
        cities = [*to_save[country]]
        for city in cities:
            for year in range(2017, current_year + 1):
                for key in [*allkeys]:
                    if to_save[country][city][str(year)][key] == None:
                        to_save[country][city][str(year)][key] = rand_dists[country][allkeys[key]][random.randint(0, 14)]
                    to_save[country][city][str(year)][key] = round(((to_save[country][city][str(year)][key] - means_general[allkeys[key]][0]) / st_devs_general[allkeys[key]][0]), 2)
    
    print("Data collection completed. Removed countries: " + ', '.join(skipped))
    calc_response(to_save, countries, current_year)


def add_null_values(to_save, current_year):
    print("Processing data...")
    allkeys = ["cost_of_living_index", "rent_index",
               "groceries_index", "restaurant_price_index", "local_ppi_index", "crime_index", "safety_index", "qol_index", "ppi_index", "health_care_index",
               "traffic_commute_index", "pollution_index", "climate_index",  "gross_rental_yield_centre",
               "gross_rental_yield_out", "price_to_rent_centre", "price_to_rent_out", "affordability_index"]
    countries = [*to_save]
    for country in countries:
        cities = [*to_save[country]]
        for city in cities:
            for year in range(2017, current_year + 1):
                if str(year) not in to_save[country][city]:
                    to_save[country][city][str(year)] = {}
                for key in allkeys:
                    if key not in to_save[country][city][str(year)]:
                        to_save[country][city][str(year)][key] = None
    generate_missing(to_save, current_year, countries)


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
                    to_save[city[1]] = {city[0]: {str(year): {}}}
                elif not(city[0] in to_save[city[1]]):
                    to_save[city[1]][city[0]] = {str(year): {}}
                elif not(str(year) in to_save[city[1]][city[0]]):
                    to_save[city[1]][city[0]][str(year)] = {}

                if cont == 0:
                    db_keys = ["cost_of_living_index", "rent_index",
                               "groceries_index", "restaurant_price_index", "local_ppi_index"]
                elif cont == 1:
                    db_keys = ["crime_index", "safety_index"]
                elif cont == 2:
                    db_keys = ["qol_index", "ppi_index", "health_care_index",
                               "traffic_commute_index", "pollution_index", "climate_index"]
                else:
                    db_keys = ["gross_rental_yield_centre", "gross_rental_yield_out",
                               "price_to_rent_centre", "price_to_rent_out", "affordability_index"]

                for i in range(len(db_keys)):
                    to_save[city[1]][city[0]][str(year)][db_keys[i]] = float(city_data[i])
            print(str(year) + " done")
            trusty_sleep(random.randint(2, 5))
        cont += 1
        print(link + " done")
        trusty_sleep(random.randint(2, 5))

    add_null_values(to_save, current_year)

scrape()