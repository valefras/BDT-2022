
from pyparsing import col
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import time, sleep
import random
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import stddev, avg, when

spark = SparkSession \
    .builder \
    .appName("BDT2022") \
    .getOrCreate()

to_scrape = [
    "https://www.numbeo.com/cost-of-living",
    "https://www.numbeo.com/crime",
    # "https://www.numbeo.com/quality-of-life",
    # "https://www.numbeo.com/property-investment"
]


def trusty_sleep(n):
    start = time()
    while (time() - start < n):
        sleep(n - (time() - start))


def getUrl(main_link, year):
    return main_link + "/region_rankings.jsp?title=" + str(year) + "&region=150"


# def scrape():
if datetime.now().month <= 2:
    current_year = datetime.now().year-1
else:
    current_year = datetime.now().year

cont = 0
dataf = None
for link in to_scrape:
    if cont == 0:
        var_values = ["city", "country", "year", "cost_of_living_index", "rent_index",
                      "groceries_index", "restaurant_price_index", "local_ppi_index"]
        var_keys = [2, 3, 5, 6, 7]
    elif cont == 1:
        var_values = ["city", "country", "year",
                      "crime_index", "safety_index"]
        var_keys = [2, 3]
    elif cont == 2:
        var_values = ["city", "country", "year", "qol_index", "ppi_index", "health_care_index",
                      "traffic_commute_index", "pollution_index", "climate_index"]
        var_keys = [2, 3, 5, 8, 9, 10]
    else:
        var_values = ["city", "country", "year", "gross_rental_yield_centre", "gross_rental_yield_out",
                      "price_to_rent_centre", "price_to_rent_out", "affordability_index"]
        var_keys = [3, 4, 5, 6, 8]

    print("Starting " + link)
    inter_data = []
    for year in range(2017, 2019):  # current_year + 1):
        page = requests.get(getUrl(link, year))
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="t2")
        rows = results.find_all("tr")

        for entry in rows[1:]:
            datapoints = entry.find_all('td')

            city_data = [float(entry.get_text().strip().splitlines()[i-1])
                         for i in var_keys]

            city = entry.get_text().strip().splitlines()[0].split(', ')
            city.append(year)
            city.extend(city_data)

            inter_data.append(city)
    if cont == 0:
        dataf = spark.createDataFrame(inter_data, schema=var_values)
    else:
        dataf = dataf.join(spark.createDataFrame(inter_data, schema=var_values), [
            'city', 'country', 'year'], how='outer')
    print(str(year) + " done")
    trusty_sleep(random.randint(2, 5))
    cont += 1
    print(link + " done")
dataf.show(n=5)
dataf.schema
print('Data extracted.')
# data_processing(dataf)


# def data_processing(dataf):
print('Starting data processing and generation...')

dataf.createOrReplaceTempView("city_data")
# countries = spark.sql("SELECT DISTINCT country FROM city_data")
# coun_list = countries.select('country').rdd.flatMap(lambda x: x).collect()
# for country in coun_list:
country = None
for variable in dataf.schema.names[3:]:
    # country_distributions = {}
    # null_count = spark.sql(
    #     f"SELECT city, country, year FROM city_data WHERE {variable} IS NULL").show()
    # mean_sd = spark.sql(
    #     f"SELECT AVG({variable}), STDEV({variable}), country FROM city_data WHERE country={}").show()
    # for city coutrnu yeaar
    #     UPDAte where
    # # countries = spark.sql(
    # #     f"SELECT country FROM city_data WHERE {variable} IS NULL GROUP BY country").show()
    # # sample2 = sample.rdd.map(lambda x: (x.name, x.age, x.city))
    # countries = null_count.select("country").distinct.show()

    # def fill_col():
    #     np.random.normal(mu, sigma)
    # dataf.fillna(0, subset=[variable]).show()
    # dataf.filter()
    # dataf.where(Column("price_to_rent_centre").isNull()).show()

    #s = np.random.normal(mu, sigma, n_null)

    # to_process = spark.sql(
    #     f"SELECT AVG({variable}), STDEV({variable}), country FROM city_data WHERE {variable} IS NOT NULL GROUP BY country")

    # scrape()

    null_count = spark.sql(
        f"SELECT country FROM city_data WHERE {variable} IS NULL GROUP BY country").select('country').rdd.flatMap(lambda x: x).collect()
    # to_process = spark.sql(
    #     f"SELECT AVG({variable}), STDEV({variable}), country FROM city_data WHERE {variable} IS NOT NULL GROUP BY country")
    mean_std = dataf.groupBy("country").agg(avg(variable).alias(
        'avg'), stddev(variable).alias('std'))  # .filter(dataf.groupBy("country").count(when(col(variable).isNull()))).show(5)

    # .select(
    #     col('country'),
    #     _mean(col(variable)).alias('mean'),
    #     _stddev(col(variable)).alias('std'),
    # ).collect()
    #to_process_dict = to_process.toPandas().set_index('country').T.to_dict('list')
    city_info = spark.sql(
        f"SELECT city, country, year FROM city_data WHERE {variable} IS NULL").select(['city', 'country', 'year']).rdd.map(lambda row: row.asDict()).collect()
    # .select(['city', 'country', 'year']).rdd.flatMap(lambda x: x).collect()

    for i in city_info:
        avg_country = mean_std.select('avg').filter(
            mean_std('country') == i['country']).head()[0]
        std_country = mean_std.select('std').filter(
            mean_std('country') == i['country']).head()[0]

        normal_dist = round(np.random.normal(avg_country, std_country), 2)

        update_city = i['city']
        update_country = i['country']
        update_year = i['year']

        dataf = dataf.withColumn(variable, when((col('country') == update_country) & (col(
            'city') == update_city) & (col('year') == update_year), normal_dist).otherwise(0))
        # spark.sql(
        #     f"UPDATE city_data SET {variable}={normal_dist} WHERE country='{update_country}' AND city='{update_city}' AND year={update_year}")

dataf.show()
# avg = to_process[list(zip(*to_process))
#                  [3].index(null_count[i][1])][1]
# stdev = to_process[list(zip(*to_process))
#                    [3].index(null_count[i][1])][2]
# update dei valori dalla normale
