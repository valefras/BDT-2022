require("dotenv").config();
var sanitizeUrl = require("@braintree/sanitize-url").sanitizeUrl;

const fastify = require("fastify")({
  logger: false, // Set to true to get console logs
});

const knex = require("knex")({
  client: "mysql",
  connection: {
    host: process.env.HOST,
    port: process.env.PORT,
    user: process.env.USER,
    password: process.env.LOCALHOST_PASSWORD,
    database: "bd2022",
  },
});

var redis = require("redis");
if (process.env.REDIS_PORT != "" && process.env.REDIS_HOST != "") {
  var client = redis.createClient({
    url: "redis://" + process.env.REDIS_HOST + ":" + process.env.REDIS_PORT,
    username: process.env.REDIS_USERNAME,
    password: process.env.REDIS_PASS,
  });
} else {
  var client = redis.createClient();
}
client.connect();
client.on("error", (err) => console.log("Redis Client Error", err));

// Get all the cities of a country for a given year
fastify.get("/country", async function (request, reply) {
  reply.header("Access-Control-Allow-Origin", "*");
  reply.header("Access-Control-Allow-Methods", "GET");
  if (
    request.query.year &&
    request.query.year != "" &&
    request.query.name &&
    request.query.name != ""
  ) {
    let year = sanitizeUrl(request.query.year);
    let country = sanitizeUrl(request.query.name);
    let toRtn = { year: year, country: country, cities: {} };
    let key = "country:" + country + ":" + year;
    //await client.del(key)
    let results = await client.get(key);
    /* await client.ttl(key).then(res=>{
            console.log(res)
        }) */
    if (!results) {
      await knex("main_data")
        .where({
          year: year,
          country: country,
        })
        .orderBy("city")
        .select("*")
        .then(function (rows) {
          for (let i = 0; i < rows.length; i++) {
            delete rows[i].country;
            delete rows[i].year;
            toRtn.cities[rows[i].city] = JSON.parse(JSON.stringify(rows[i]));
            delete toRtn.cities[rows[i].city].city;
          }
          reply
            .code(200)
            .header("Content-Type", "application/json")
            .send(toRtn);
          if (rows.length > 0) {
            client.set(key, JSON.stringify(toRtn), {
              EX: 3600,
            });
          }
        });
    } else {
      //console.log("REDIS")
      reply
        .code(200)
        .header("Content-Type", "application/json")
        .send(JSON.parse(results));
    }
  } else {
    reply.send({ status: 200, error: "Invalid query" });
  }
});

// Get the average predictions for all countries for a given year
fastify.get("/predictions/summary", async function (request, reply) {
  reply.header("Access-Control-Allow-Origin", "*");
  reply.header("Access-Control-Allow-Methods", "GET");
  if (request.query.year && request.query.year != "") {
    let year = sanitizeUrl(request.query.year);
    let toRtn = { year: year, countries: {} };
    let key = "preds:summary:" + year;
    let results = await client.get(key);
    if (!results) {
      await knex
        .select("country", knex.raw("AVG(y)"))
        .from("predictions")
        .where({
          year: year,
        })
        .groupBy("country")
        .then(function (rows) {
          for (let i = 0; i < rows.length; i++) {
            toRtn.countries[rows[i].country] = parseFloat(
              rows[i]["AVG(y)"].toFixed(3)
            );
          }
          reply
            .code(200)
            .header("Content-Type", "application/json")
            .send(toRtn);
          if (rows.length > 0) {
            client.set(key, JSON.stringify(toRtn), {
              EX: 3600,
            });
          }
        });
    } else {
      //console.log("REDIS")
      reply
        .code(200)
        .header("Content-Type", "application/json")
        .send(JSON.parse(results));
    }
  } else {
    reply.send({ status: 200, error: "Invalid query" });
  }
});

// Get the historical and forecast investment indices for all the cities of a certain country
fastify.get("/predictions/full", async function (request, reply) {
  reply.header("Access-Control-Allow-Origin", "*");
  reply.header("Access-Control-Allow-Methods", "GET");
  if (request.query.country && request.query.country != "") {
    let country = sanitizeUrl(request.query.country);
    let toRtn = {};
    let key = "preds:full:" + country;
    let results = await client.get(key);
    if (!results) {
      await knex
        .select("city", "y", "year")
        .from("predictions")
        .where({
          country: country,
        })
        .union([
          knex.select("city", "y", "year").from("main_data").where({
            country: country,
          }),
        ])
        .then(function (rows) {
          for (let i = 0; i < rows.length; i++) {
            if (!toRtn[rows[i].city]) {
              toRtn[rows[i].city] = {};
            }
            toRtn[rows[i].city][rows[i].year] = rows[i].y;
          }
          reply
            .code(200)
            .header("Content-Type", "application/json")
            .send(toRtn);
          if (rows.length > 0) {
            client.set(key, JSON.stringify(toRtn), {
              EX: 3600,
            });
          }
        });
    } else {
      //console.log("REDIS")
      reply
        .code(200)
        .header("Content-Type", "application/json")
        .send(JSON.parse(results));
    }
  } else {
    reply.send({ status: 200, error: "Invalid query" });
  }
});

// Get all the y for all the years in the DB (both real and predicted) for a certain country
fastify.get("/responses/full", async function (request, reply) {
  reply.header("Access-Control-Allow-Origin", "*");
  reply.header("Access-Control-Allow-Methods", "GET");
  if (request.query.country && request.query.country != "") {
    let country = sanitizeUrl(request.query.country);
    let toRtn = {};
    let key = "y:" + country;
    let results = await client.get(key);
    if (!results) {
      await knex
        .unionAll([
          knex
            .select("main_data.year", knex.raw("AVG(main_data.y) AS y"))
            .from("main_data")
            .where({ country: country })
            .groupBy("year"),
          knex
            .select("predictions.year", knex.raw("AVG(predictions.y) AS y"))
            .from("predictions")
            .where({ country: country })
            .groupBy("year"),
        ])
        .then(function (rows) {
          for (let i = 0; i < rows.length; i++) {
            toRtn[rows[i].year] = rows[i].y;
          }
          reply
            .code(200)
            .header("Content-Type", "application/json")
            .send(toRtn);
          if (rows.length > 0) {
            client.set(key, JSON.stringify(toRtn), {
              EX: 3600,
            });
          }
        });
    } else {
      //console.log("REDIS")
      reply
        .code(200)
        .header("Content-Type", "application/json")
        .send(JSON.parse(results));
    }
  } else {
    reply.send({ status: 200, error: "Invalid query" });
  }
});

const start = async () => {
  try {
    await fastify.listen({ port: 3000, host: "0.0.0.0" });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};
start();
