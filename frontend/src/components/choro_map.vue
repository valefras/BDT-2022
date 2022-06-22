<template>
  <l-map
    ref="map"
    id="map"
    :center="center"
    :zoom="3"
    :minZoom="3"
    :maxZoom="6"
    :options="mapOptions"
  >
    <l-choropleth-layer
      :data="countryData"
      titleKey="country"
      idKey="country"
      :value="value"
      geojsonIdKey="geounit"
      :geojson="geo"
      :colorScale="colorScale"
      :click="showCountry"
    >
      <template slot-scope="props">
        <l-info-control
          :item="props.currentItem"
          :unit="props.unit"
          title="Country information"
          placeholder="Hover/tap a country"
        />
        <l-reference-chart
          title="Future European investment ratings"
          :colorScale="colorScale"
          :min="props.min"
          :max="props.max"
          position="topright"
        />
      </template>
    </l-choropleth-layer>
  </l-map>
</template>

<script>
import { LMap /*LTileLayer, LMarker*/ } from "vue2-leaflet";
import { InfoControl, ReferenceChart } from "vue-choropleth";
import ChoroplethLayer from "./ChoroplethLayer";
export default {
  name: "choro_map",
  props:{
    center: Array,
    countryData: Array,
    geo: Object,
    value: Object,
    colorScale: Array,
    mapOptions: Object
  },
  components: {
    LMap,
    //LTileLayer,
    //LMarker,
    "l-info-control": InfoControl,
    "l-reference-chart": ReferenceChart,
    "l-choropleth-layer": ChoroplethLayer,
  },
  methods:{
    showCountry(country){
        this.$emit("showCountry", country)
    }
  }
};
</script>

<style scoped>
@media (min-height: 780px) {
  #map {
    height: 600px;
  }
}
@media (max-height: 780px) {
  #map {
    height: 500px;
  }
}
@media (max-height: 650px) {
  #map {
    height: 400px;
  }
}
</style>