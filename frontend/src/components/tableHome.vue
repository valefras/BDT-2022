<template>
  <div class="overflow-x-auto">
    <table class="mx-auto">
      <thead>
        <tr class="uppercase tbl-head">
          <th class="px-2" @click="sort('city')">
            <span>city</span>
            <span>
              <svg
                v-if="currentSort != 'city'"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path
                  d="M12 5.83L15.17 9l1.41-1.41L12 3 7.41 7.59 8.83 9 12 5.83zm0 12.34L8.83 15l-1.41 1.41L12 21l4.59-4.59L15.17 15 12 18.17z"
                />
              </svg>
              <svg
                v-else-if="currentSortDir == 'desc'"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z" />
              </svg>
            </span>
          </th>
          <th class="px-2" v-for="x in keys" :key="x" @click="sort(x)">
            <span>{{ parsed_keys[x] }}</span>
            <span>
              <svg
                v-if="currentSort != x"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path
                  d="M12 5.83L15.17 9l1.41-1.41L12 3 7.41 7.59 8.83 9 12 5.83zm0 12.34L8.83 15l-1.41 1.41L12 21l4.59-4.59L15.17 15 12 18.17z"
                />
              </svg>
              <svg
                v-else-if="currentSortDir == 'desc'"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path d="M0 0h24v24H0z" fill="none" />
                <path d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z" />
              </svg>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in cities" :key="c.metrics.id" class="bg-change">
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
      cities: [],
      currentSortDir: "asc",
      currentSort: "city",
    };
  },
  created() {
    this.cities = this.currentCountry;
  },
  methods: {
    sort(s) {
      console.log(s);
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === "asc" ? "desc" : "asc";
      } else {
        this.currentSortDir = "desc";
      }
      this.currentSort = s;
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
  watch: {
    currentCountry(country) {
      this.cities = country;
    },
  },
};
</script>

<style scoped>
.mx-auto {
  margin-left: auto;
  margin-right: auto;
}
.overflow-x-auto {
  overflow-x: auto;
}
.p-1 {
  padding: 0.15rem;
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
svg {
  width: 24px;
  height: 24px;
  fill: white;
}
th > span {
  display: block;
}
</style>
