from .database_setup import connect
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql.types import *
import pyspark.sql.functions as F
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import udf
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StandardScaler
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import time, sleep
import random
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("BDT2022") \
    .config('spark.driver.host', '127.0.0.1') \
    .getOrCreate()

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


def scrape():
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
        for year in range(2017, current_year + 1):
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
            print(str(year) + " done")
            trusty_sleep(random.randint(2, 5))

        if cont == 0:
            dataf = pd.DataFrame(inter_data, columns=var_values)
            # dataf = spark.createDataFrame(inter_data, schema=var_values)
        else:
            dataf = pd.merge(pd.DataFrame(inter_data, columns=var_values),
                             dataf, how='outer', on=['city', 'country', 'year'])
            # dataf = dataf.join(spark.createDataFrame(inter_data, schema=var_values), [
            #   'city', 'country', 'year'], how='outer')
        # trusty_sleep(random.randint(2, 5))
        cont += 1
        print(link + " done")
    return fill_missing(dataf)


def fill_missing(dataf):
    print('Filling missing values...')
    listColumns = list(dataf.columns)
    listColumns.remove('year')
    avg_df = dataf.groupby('country')[listColumns].mean()
    std_df = dataf.groupby('country')[listColumns].std()
    cities = dataf.city.unique()
    years = dataf.year.unique()

    for year in years:
        for city in cities:
            if not (dataf["city"][(dataf['year'] == int(year))] == city).any().all():
                to_insert = [city, dataf[dataf.city == city].iloc[0].country, year]
                to_insert.extend([None for i in range(18)])
                dataf.loc[len(dataf.index)] = to_insert
    for variable in dataf.columns[3:]:
        dataf[variable] = dataf.apply(lambda x: round(np.random.normal(avg_df.loc[x['country']][variable], std_df.loc[x['country']][variable]), 2) if pd.isnull(
            x[variable]) else x[variable], axis=1)

    filled_dataf = dataf.dropna()
    return normalize_data(filled_dataf)


def normalize_data(filled_dataf):
    print('Normalizing values...')
    spark_dataf = spark.createDataFrame(filled_dataf)
    # spark_dataf.printSchema()

    """ colnames = spark_dataf.schema.names[3:]
    vecAssembler = VectorAssembler(
        inputCols=colnames, outputCol="features", handleInvalid='skip')
    normalizer = StandardScaler(
        inputCol="features", outputCol="scaledFeatures")
    pipeline_normalize = Pipeline(stages=[vecAssembler, normalizer])
    df_transf = pipeline_normalize.fit(spark_dataf).transform(spark_dataf)
    to_array = F.udf(lambda x: (x.toArray().tolist()), ArrayType(DoubleType()))
    df_array = df_transf.withColumn(
        "scaledFeatures", to_array("scaledFeatures"))
    df_final = df_array.select([F.col('city'), F.col('country'), F.col('year')]+[F.round(F.col('scaledFeatures')[i], 3).alias(
        colnames[i]) for i in range(len(colnames))]) """
    df_final = spark_dataf
    df_final_y = df_final.withColumn("y", F.round(df_final["cost_of_living_index"]*-1+df_final["rent_index"]*1+df_final["groceries_index"]*-0.5+df_final["restaurant_price_index"]*-0.5+df_final["local_ppi_index"]*1+df_final["crime_index"]*-1+df_final["safety_index"]*1+df_final["qol_index"]*1+df_final["ppi_index"]*1 +
                                                  df_final["health_care_index"]*1+df_final["traffic_commute_index"]*-0.5+df_final["pollution_index"]*-1+df_final["climate_index"]*0.5+df_final["gross_rental_yield_centre"]*1+df_final["gross_rental_yield_out"]*1+df_final["price_to_rent_centre"]*-1+df_final["price_to_rent_out"]*-1+df_final["affordability_index"]*1, 3))
    return insert_DB(df_final_y)


def insert_DB(df_final_y):
    print("Pushing data to database...")
    conn = connect()
    to_upload = df_final_y.toPandas()
    to_upload.to_sql(con=conn, name='main_data',
                     if_exists='append', index=False)
    db_conn = conn.connect()
    db_conn.close()
    return to_upload
