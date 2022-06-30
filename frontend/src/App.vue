<template>
  <div id="app" class="container">
    <!--
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </nav>
    -->
    <router-view />
  </div>
</template>

<style>
/*
* Palette https://digitalsynopsis.com/wp-content/uploads/2017/07/website-color-schemes-palettes-combinations-1b.jpg
* background: #17252A
* azure-dark: #2B7A78
* azure-light: #3AAFA9
* dirty-white: #DEF2F1
* white: #FEFFFF
*/
:root {
  --background: #17252a;
  --hover: #134e4a;
  --azure-dark: #2b7a78;
  --azure-light: #3aafa9;
  --dirty-white: #def2f1;
  --link: #60fff7;
  --header: #3aafa9;
  --white: #feffff;
}
#app {
  width: 100%;
}
body {
  background-color: var(--background);
  color: var(--white);
  margin: 0;
  padding: 1em;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}
a {
  color: var(--link);
}
.container {
  max-width: 100%;
  margin: 0 auto;
}
@media (min-width: 640px) {
  .container {
    max-width: 640px;
  }
}
@media (min-width: 768px) {
  .container {
    max-width: 768px;
  }
}
@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
  }
}
@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
@media (min-width: 1536px) {
  .container {
    max-width: 1536px;
  }
}

@media (max-width: 500px) {
  .leaflet-control {
    color: black;
    font-size: 10pt !important;
  }
}
@media (min-width: 501px) {
  .leaflet-control {
    color: black;
    font-size: 12pt !important;
  }
}
h1,
h2,
h3,
h4 {
  color: var(--header);
}
th {
  font-weight: 400;
}
</style>
