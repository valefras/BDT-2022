<template>
  <div>
    <h1>Long term European real estate</h1>
    <div style="margin: 1em 0">
      <span>Forecast for the year: </span>
      <span class="select-dropdown">
        <select v-model="selectedPrediction">
          <option value="2023">2023</option>
          <option value="2024">2024</option>
        </select>
      </span>
    </div>
    <choro
      v-if="showChoro"
      :center="center"
      :countryData="countryData"
      :geo="geo"
      :value="value"
      :colorScale="colorScale"
      :mapOptions="mapOptions"
      @showCountry="showCountry"
    />
    <div>
      <h2>
        More information
        <span v-if="selectedCountry">on {{ selectedCountry }}</span>
      </h2>
      <p v-if="!show">Click on a country to see detailed information</p>
      <div v-else>
        <div class="grid">
          <div>
            <h3>Historical + forecast investment index (by city)</h3>
            <tableHome
              :keys="trendKeys"
              :parsed_keys="trendParsedKeys"
              :currentCountry="trendCurrentCountry"
            />
          </div>
          <div>
            <h3>Historical + forecast investment index (country mean)</h3>
            <div id="plot">
              <LineChartGenerator
                :chart-options="chartOptions"
                :chart-data="chartData"
                :chart-id="'plot'"
                :dataset-id-key="'label'"
                :width="400"
                :height="200"
                :styles="{ backgroundColor: 'white' }"
              />
            </div>
          </div>
        </div>
        <h3>Historical data</h3>
        <div style="margin-bottom: 0.75em">
          <span>Year: </span>
          <span class="select-dropdown">
            <select v-model="selectedInfo">
              <option value="2022">2022</option>
              <option value="2021">2021</option>
              <option value="2020">2020</option>
              <option value="2019">2019</option>
              <option value="2018">2018</option>
              <option value="2017">2017</option>
            </select>
          </span>
        </div>
        <h4>Country summary</h4>
        <ul>
          <li>Country: {{ selectedCountry }}</li>
          <li v-for="key in summaryKeys" :key="key">
            {{ key == "y" ? "Investment rating" : parsed_keys[key] }}:
            {{ currentSummary[key] }}
          </li>
        </ul>
        <h4>Cities overview</h4>
        <tableHome
          :keys="keys"
          :parsed_keys="parsed_keys"
          :currentCountry="currentCountry"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import choro from "@/components/choro_map.vue";
//import { countryData } from "../assets/new_scraped_results";
import geo from "../assets/custom.geo.json";
import tableHome from "@/components/tableHome.vue";
import { Line as LineChartGenerator } from "vue-chartjs/legacy";
import {
  Chart as ChartJS,
  Title,
  PointElement,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  PointElement,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale
);

export default {
  name: "home-view",
  components: {
    choro,
    tableHome,
    LineChartGenerator,
  },
  data() {
    return {
      first: true,
      countryData: [],
      showChoro: false,
      center: [55, 25],
      selectedPrediction: "2023",
      selectedInfo: "2022",
      selectedCountry: "",
      currentSummary: {},
      chartData: {
        labels: [],
        datasets: [],
      },
      trendTable: [],
      firstCity: "",
      pointBackgroundColor: [
        //fare il fill dell'array in automatico quando riceviamo la risposta API
        "#2b7a78",
        "#2b7a78",
        "#2b7a78",
        "#2b7a78",
        "#2b7a78",
        "#2b7a78",
        "#F15412",
        "#F15412",
      ],
      chartOptions: {
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: "",
            font: { size: 14 },
          },
        },
      },
      geo,
      value: {
        key: "y",
        metric: "investment rating",
      },
      colorScale: ["af3a40", "3aafa9"],
      mapOptions: {
        attributionControl: false,
        scrollWheelZoom: false,
      },
      currentCountry: [],
      trendCurrentCountry: [],
      trendParsedKeys: {},
      trendKeys: [],
      summaryKeys: [
        "y",
        "cost_of_living_index",
        "rent_index",
        "ppi_index",
        "gross_rental_yield_centre",
        "gross_rental_yield_out",
        "price_to_rent_centre",
        "price_to_rent_out",
        "affordability_index",
      ],
      keys: [
        //ricavare le keys da API?
        "y",
        "cost_of_living_index",
        "rent_index",
        "groceries_index",
        "restaurant_price_index",
        "local_ppi_index",
        "crime_index",
        "safety_index",
        "qol_index",
        "ppi_index",
        "health_care_index",
        "traffic_commute_index",
        "pollution_index",
        "climate_index",
        "gross_rental_yield_centre",
        "gross_rental_yield_out",
        "price_to_rent_centre",
        "price_to_rent_out",
        "affordability_index",
      ],
      parsed_keys: {
        //fare il parse in automatico, magari con regex?
        y: "Investment rating",
        cost_of_living_index: "Cost of living",
        rent_index: "Rent",
        groceries_index: "Groceries",
        restaurant_price_index: "Restaurant price",
        local_ppi_index: "Local purchasing power",
        crime_index: "Crime",
        safety_index: "Safety",
        qol_index: "Quality of life",
        ppi_index: "Purchasing power",
        health_care_index: "Health care",
        traffic_commute_index: "Traffic commute time",
        pollution_index: "Pollution",
        climate_index: "Climate",
        gross_rental_yield_centre: "Gross rental yield (centre)",
        gross_rental_yield_out: "Gross rental yield (out)",
        price_to_rent_centre: "Price to rent (centre)",
        price_to_rent_out: "Price to rent (out)",
        affordability_index: "Affordability",
      },
    };
  },
  created() {
    /*
    if (window.screen.width >= 800) {
      this.center = [55,55]
    }
    else{
      this.center = [55,25]
    }
    */
    this.loadChoro();
  },
  computed: {
    show() {
      if (this.first) {
        return this.currentCountry.length != 0;
      }
      return true;
    },
  },
  methods: {
    loadChoro() {
      //this.showChoro = false;
      this.countryData = [];
      axios
        .get(
          "http://127.0.0.1:3000/predictions/summary?year=" +
            this.selectedPrediction
        )
        .then((res) => {
          let countries = Object.keys(res.data.countries);
          for (let i = 0; i < countries.length; i++) {
            this.countryData.push({
              id: i,
              country: countries[i],
              y: res.data.countries[countries[i]],
            });
          }
          this.showChoro = true;
        });
    },
    showCountry(country) {
      this.currentCountry = [];
      let countryArr = [];
      axios
        .get(
          "http://127.0.0.1:3000/country?name=" +
            country.name +
            "&year=" +
            this.selectedInfo
        )
        .then((res) => {
          let cities = Object.keys(res.data.cities);
          for (let i = 0; i < this.summaryKeys.length; i++) {
            this.currentSummary[this.summaryKeys[i]] = 0;
          }
          for (let i = 0; i < cities.length; i++) {
            countryArr.push({
              city: cities[i],
              country: country.name,
              metrics: res.data.cities[cities[i]],
            });
            for (let j = 0; j < this.summaryKeys.length; j++) {
              this.currentSummary[this.summaryKeys[j]] +=
                res.data.cities[cities[i]][this.summaryKeys[j]];
            }
          }
          for (let i = 0; i < this.summaryKeys.length; i++) {
            this.currentSummary[this.summaryKeys[i]] = (
              this.currentSummary[this.summaryKeys[i]] / cities.length
            )
              .toFixed(3)
              .replace(/0+$/, "");
          }
        })
        .then(() => {
          this.currentCountry = countryArr;
        })
        .catch((err) => {
          console.error(err);
        });
      this.selectedCountry = country.name;
      this.showChart();
      this.first = false;
    },
    showChart() {
      axios
        .get(
          "http://127.0.0.1:3000/responses/full?country=" + this.selectedCountry
        )
        .then((res) => {
          this.chartData.labels = Object.keys(res.data);
          this.chartOptions.plugins.title.text =
            this.selectedCountry + " buying indexes (cities mean)";
          let dataChart = [];
          for (let i = 0; i < this.chartData.labels.length; i++) {
            dataChart.push(res.data[this.chartData.labels[i]]);
          }
          this.chartData.datasets = [
            {
              label: "Buying index",
              pointBackgroundColor: this.pointBackgroundColor,
              radius: 5,
              data: dataChart,
            },
          ];
        })
        .catch((err) => {
          console.error(err);
        });
      this.showTrend();
    },
    showTrend() {
      this.trendCurrentCountry = [];
      axios
        .get(
          "http://127.0.0.1:3000/predictions/full?country=" +
            this.selectedCountry
        )
        .then((res) => {
          this.trendTable = res.data;
          this.firstCity = Object.keys(this.trendTable)[0];
          for (let i = 0; i < Object.keys(this.trendTable).length; i++) {
            this.trendCurrentCountry.push({
              city: Object.keys(this.trendTable)[i],
              country: this.selectedCountry,
              metrics: this.trendTable[Object.keys(this.trendTable)[i]],
            });
          }

          this.trendKeys = Object.keys(this.trendTable[this.firstCity]);

          this.trendParsedKeys = Object.assign(
            ...Object.keys(
              this.trendTable[Object.keys(this.trendTable)[0]]
            ).map((k, i) => ({
              [k]: Object.keys(
                this.trendTable[Object.keys(this.trendTable)[0]]
              )[i],
            }))
          );
        })

        .catch((err) => {
          console.error(err);
        });
    },
  },
  watch: {
    selectedPrediction() {
      this.loadChoro();
    },
    selectedInfo() {
      this.showCountry({ name: this.selectedCountry });
      this.showTrend({ name: this.selectedCountry });
    },
  },
};
</script>

<style scoped>
.grid {
  display: grid;
  gap: 20px;

  grid-template-columns: 1fr 1fr;
}
.select-dropdown,
.select-dropdown * {
  margin: 0;
  padding: 0;
  position: relative;
  width: max-content;
}
.select-dropdown {
  position: relative;
  border-radius: 4px;
  background-color: #2b7a78;
}
.select-dropdown select {
  font-size: 1rem;
  border-radius: 4px;
  font-weight: normal;
  color: var(--white);
  max-width: 100%;
  padding: 8px 24px 8px 10px;
  border: none;
  background-color: var(--azure-dark);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
.select-dropdown select:active,
.select-dropdown select:focus {
  outline: none;
  box-shadow: none;
}
.select-dropdown:after {
  content: "";
  position: absolute;
  top: 50%;
  right: 8px;
  width: 0;
  height: 0;
  margin-top: -2px;
  border-top: 5px solid #aaa;
  border-right: 5px solid transparent;
  border-left: 5px solid transparent;
}

@media (min-width: 768px) {
  #plot {
    max-width: 768px;
  }
}
@media (max-width: 1200px) {
  .grid {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
