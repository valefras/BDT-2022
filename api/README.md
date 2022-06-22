# BDT-2022 Rest API
To start the api, simply install the needed dependencies with 'npm i' and then run the script with 'node index.js'.

## Endpoints
- /country?name=[insert_name]&year=[insert_year] = get all the cities of a country for a given year
- /predictions/summary?year=[insert_year] = get the average predictions for all countries for a given year
- /predictions/full?year=[insert_year]&country=[insert_country] = get the predictions for all the cities of a certain country for a given year
- /responses/full?country=[insert_country] = get all the y for all the years in the DB (both real and predicted) for a certain country