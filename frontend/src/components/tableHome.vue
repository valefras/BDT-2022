<template>
  <div class="overflow-x-auto">
    <table class="">
      <thead>
        <tr class="uppercase tbl-head">
          <th class="px-2" @click="sort('city')">city</th>
          <th class="px-2" v-for="x in keys" :key="x" @click="sort(x)">
            {{ parsed_keys[x] }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in cities" :key="c.city" class="bg-change">
          <td class="p-1 px-2">{{ c.city }}</td>
          <td class="p-1 px-2" v-for="k in keys" :key="c.city + k">
            {{ c.metrics[k] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "tableHome",
  props: {
    keys: Array,
    currentCountry: Array,
    parsed_keys: Object,
  },
  data() {
    return {
      cities: this.currentCountry,
      currentSortDir: "asc",
      currentSort: "city",
    };
  },
  methods: {
    sort(s) {
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === "asc" ? "desc" : "asc";
      } else {
        this.currentSortDir = "asc";
      }
      this.currentSort = s;
      //questo dopo va snellito quando abbiamo i dati finali, non avremo più il controllo se il sort è city o meno
      this.cities = this.cities.slice().sort((a, b) => {
        let modifier = 1;
        if (this.currentSortDir === "desc") modifier = -1;
        if (this.currentSort == "city") {
          if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
          if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier;
        } else {
          if (a["metrics"][this.currentSort] < b["metrics"][this.currentSort])
            return -1 * modifier;
          if (a["metrics"][this.currentSort] > b["metrics"][this.currentSort])
            return 1 * modifier;
        }
        return 0;
      });
    },
  },
};
</script>

<style scoped>
.overflow-x-auto {
  overflow-x: auto;
}
.p-1 {
  padding: 0.25rem; /* 4px */
}
.tbl-head {
  background-color: var(--azure-dark);
}
.px-2 {
  padding-left: 0.5rem; /* 8px */
  padding-right: 0.5rem; /* 8px */
}
.uppercase {
  text-transform: uppercase;
}
.bg-change:hover {
  background-color: var(--hover);
}
</style>