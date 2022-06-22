<template>
  <div>
    <div style="margin: 1em 0">
      <span>Predictions for the year: </span>
      <span class="select-dropdown">
        <select v-model="selectedPrediction">
          <option value="2023">2023</option>
          <option value="2024">2024</option>
        </select>
      </span>
    </div>
    <choro
      :center="center"
      :countryData="countryData"
      :geo="geo"
      :value="value"
      :colorScale="colorScale"
      :mapOptions="mapOptions"
      @showCountry="showCountry"
    />
    <div>
      <h2>Cities information</h2>
      <div v-if="show" style="margin-bottom: 0.75em">
        <span>{{ selectedCountry }} - Year: </span>
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
      <p v-if="!show">Click on a country to see detailed information</p>
      <div v-else>
        <tableHome
          :keys="keys"
          :parsed_keys="parsed_keys"
          :currentCountry="currentCountry"
        />
        <h2>Buying indexes</h2>
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
  </div>
</template>

<script>
import choro from "@/components/choro_map.vue";
import { countryData } from "../assets/new_scraped_results";
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
      countryData,
      center: [55, 25],
      selectedPrediction: "2023",
      selectedInfo: "2022",
      selectedCountry: "",
      chartData: {
        labels: [],
        datasets: [],
      },
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
      colorScale: ["b4e4e3", "2b7a78"],
      mapOptions: {
        attributionControl: false,
        scrollWheelZoom: false,
      },
      currentCountry: [],
      keys: [
        //ricavare le keys da API?
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
        "y",
      ],
      parsed_keys: {
        //fare il parse in automatico, magari con regex?
        cost_of_living_index: "cost of living",
        rent_index: "rent",
        groceries_index: "groceries",
        restaurant_price_index: "restaurant price",
        local_ppi_index: "local purchasing power",
        crime_index: "crime",
        safety_index: "safety",
        qol_index: "quality of life",
        ppi_index: "purchasing power",
        health_care_index: "health care",
        traffic_commute_index: "traffic commute time",
        pollution_index: "pollution",
        climate_index: "climate",
        gross_rental_yield_centre: "gross rental yield (centre)",
        gross_rental_yield_out: "gross rental yield (out)",
        price_to_rent_centre: "price to rent (centre)",
        price_to_rent_out: "price to rent (out)",
        affordability_index: "affordability",
        y: "y",
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
  },
  computed: {
    show() {
      return this.currentCountry.length != 0;
    },
  },
  methods: {
    showCountry(country) {
      let countryArr = [
        {
          city: "Geneva",
          country: "Switzerland",
          metrics: {
            cost_of_living_index: 462.32,
            rent_index: 233.43,
            groceries_index: 384.52,
            restaurant_price_index: 477.13,
            local_ppi_index: 350.97,
            crime_index: -34.54,
            safety_index: 34.54,
            qol_index: 53.52,
            ppi_index: 117.82,
            health_care_index: 30.69,
            traffic_commute_index: 8.3,
            pollution_index: 337.42,
            climate_index: -3.76,
            gross_rental_yield_centre: 1.84,
            gross_rental_yield_out: -55.39,
            price_to_rent_centre: -55.24,
            price_to_rent_out: 58.54,
            affordability_index: 60.41,
            y: -377.52,
          },
        },
        {
          city: "Basel",
          country: "Switzerland",
          metrics: {
            cost_of_living_index: 447.68,
            rent_index: 134.92,
            groceries_index: 315.49,
            restaurant_price_index: 513.73,
            local_ppi_index: 294.89,
            crime_index: -76.9,
            safety_index: 76.9,
            qol_index: 66.21,
            ppi_index: 117.21,
            health_care_index: 9.8,
            traffic_commute_index: 18.71,
            pollution_index: 317.98,
            climate_index: -18.19,
            gross_rental_yield_centre: -29.64,
            gross_rental_yield_out: -49.96,
            price_to_rent_centre: -50.92,
            price_to_rent_out: 54.46,
            affordability_index: 69.74,
            y: -435.29,
          },
        },
      ];
      this.selectedCountry = country.name;
      this.chartData.labels = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
      this.chartOptions.plugins.title.text = country.name + " buying indexes";
      this.chartData.datasets = [
        {
          label: "Buying index",
          pointBackgroundColor: this.pointBackgroundColor,
          radius: 5,
          data: [100, 150, 200, 120, 150, 250, 200, 180],
        },
      ];
      this.currentCountry = countryArr;
    },
  },
};
</script>

<style scoped>
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
</style>