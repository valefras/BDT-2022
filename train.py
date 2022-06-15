import json
import pandas as pd

with open('new_scraped_results.txt') as f:
    to_insert = json.loads(f.read())

cols = {
    "year": [],
    "cost_of_living_index": [],
    "rent_index": [],
    "groceries_index": [],
    "restaurant_price_index": [],
    "local_ppi_index": [],
    "crime_index": [],
    "safety_index": [],
    "qol_index": [],
    "ppi_index": [],
    "health_care_index": [],
    "traffic_commute_index": [],
    "pollution_index": [],
    "climate_index": [],
    "gross_rental_yield_centre": [],
    "gross_rental_yield_out": [],
    "price_to_rent_centre": [],
    "price_to_rent_out": [],
    "affordability_index": [],
    "y": []
}

for city in to_insert:
    for year in [*city["metrics"]]:
        cols["year"].append(year)
        for key in [*cols][1:]:
            cols[key].append(city["metrics"][year][key])

df = pd.DataFrame(cols)