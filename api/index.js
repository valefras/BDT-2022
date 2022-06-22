require('dotenv').config()
var sanitizeUrl = require("@braintree/sanitize-url").sanitizeUrl;

const fastify = require('fastify')({
    logger: false // Set to true to get console logs
})

const knex = require('knex')({
    client: 'mysql',
    connection: {
        host: process.env.HOST_DB,
        port: process.env.PORT_DB,
        user: process.env.USER_DB,
        password: process.env.PASS_DB,
        database: 'bd2022'
    }
});

// Get all the cities of a country for a given year
fastify.get('/country', async function (request, reply) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header("Access-Control-Allow-Methods", "GET");
    if ((request.query.year && request.query.year != "") && (request.query.name && request.query.name != "")) {
        let year = sanitizeUrl(request.query.year)
        let country = sanitizeUrl(request.query.name)
        let toRtn = { year: year, country: country, cities: {} }
        await knex('main_data').where({
            year: year,
            country: country
        }).select('*').then(function (rows) {
            for (let i = 0; i < rows.length; i++) {
                delete rows[i].country
                delete rows[i].year
                toRtn.cities[rows[i].city] = JSON.parse(JSON.stringify(rows[i]));
                delete toRtn.cities[rows[i].city].city
            }
            reply
                .code(200)
                .header('Content-Type', 'application/json')
                .send(toRtn)
        })
    }
    else {
        reply.send({ status: 200, error: "Invalid query" })
    }
})

// Get the average predictions for all countries for a given year
fastify.get('/predictions/summary', async function (request, reply) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header("Access-Control-Allow-Methods", "GET");
    if (request.query.year && request.query.year != "") {
        let year = sanitizeUrl(request.query.year)
        let toRtn = { year: year, countries: {} }
        await knex.select('country', knex.raw('AVG(y)'))
            .from('predictions')
            .where({
                year: year
            })
            .groupBy('country')
            .then(function (rows) {
                for (let i = 0; i < rows.length; i++) {
                    toRtn.countries[rows[i].country] = parseFloat(rows[i]["AVG(y)"].toFixed(3));
                }
                reply
                    .code(200)
                    .header('Content-Type', 'application/json')
                    .send(toRtn)
            })
    }
    else {
        reply.send({ status: 200, error: "Invalid query" })
    }
})

// Get the predictions for all the cities of a certain country for a given year
fastify.get('/predictions/full', async function (request, reply) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header("Access-Control-Allow-Methods", "GET");
    if ((request.query.year && request.query.year != "") && (request.query.country && request.query.country != "")) {
        let year = sanitizeUrl(request.query.year)
        let country = sanitizeUrl(request.query.country)
        let toRtn = { year: year, cities: {} }
        await knex.select('city', 'y')
            .from('predictions')
            .where({
                country: country,
                year: year
            })
            .then(function (rows) {
                for (let i = 0; i < rows.length; i++) {
                    toRtn.cities[rows[i].city] = rows[i].y;
                }
                reply
                    .code(200)
                    .header('Content-Type', 'application/json')
                    .send(toRtn)
            })
    }
    else {
        reply.send({ status: 200, error: "Invalid query" })
    }
})

// Get all the y for all the years in the DB (both real and predicted) for a certain country
fastify.get('/responses/full', async function (request, reply) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header("Access-Control-Allow-Methods", "GET");
    if (request.query.country && request.query.country != "") {
        let country = sanitizeUrl(request.query.country)
        let toRtn = {}
        await knex.select('main_data.year', knex.raw('AVG(main_data.y) AS y'))
            .from('main_data')
            .where({ country: country })
            .groupBy('year', 'country')
            .union([
                knex.select('predictions.year', knex.raw('AVG(predictions.y) AS y'))
                    .from('predictions')
                    .where({ country: country })
            ])
            .then(function (rows) {
                for (let i = 0; i < rows.length; i++) {
                    toRtn[rows[i].year] = rows[i].y;
                }
                reply
                    .code(200)
                    .header('Content-Type', 'application/json')
                    .send(toRtn)
            })
    }
    else {
        reply.send({ status: 200, error: "Invalid query" })
    }
})

const start = async () => {
    try {
        await fastify.listen({ port: 3000 })
    } catch (err) {
        fastify.log.error(err)
        process.exit(1)
    }
}
start()