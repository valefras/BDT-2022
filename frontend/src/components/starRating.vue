<template>
  <div class="wrap">
    <div
      v-for="i in 5"
      :key="i"
      :class="[rating >= i * 2 ? 'setYellow' : 'setGrey']"
      class="cont"
    >
      <svg class="star">
        <defs>
          <clipPath id="maskRect1" clipPathUnits="objectBoundingBox">
            <path
              d="M0.5 0L0.612257 0.345491H0.975528L0.681636 0.559017L0.793893 0.904508L0.5 0.690983L0.206107 0.904508L0.318364 0.559017L0.0244717 0.345491H0.387743L0.5 0Z"
            />
          </clipPath>
        </defs>
      </svg>

      <span
        class="halfPad"
        :class="rating >= i * 2 - 1 ? 'setYellow' : 'setGrey'"
      ></span>
      <span
        class="halfPad"
        :class="rating >= i * 2 ? 'setYellow' : 'setGrey'"
      ></span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    rating: Number,
  },
};
</script>

<style scoped>
.wrap {
  display: flex;
  flex-direction: row;
  justify-content: center;
}
.cont {
  clip-path: url(#maskRect1);
  -webkit-clip-path: url(#maskRect1);
  height: 1rem;
  width: 1rem;
  display: flex;
  flex-direction: row;
  position: relative;
}
.halfPad {
  height: 100%;
  width: 50%;
  z-index: 10;
}
.setGrey {
  background-color: rgb(107 114 128);
}
.setYellow {
  background-color: rgb(250 204 21);
}
.star {
  position: absolute;
  z-index: 0;
  max-height: 0%;
  max-width: 0%;
}
</style>
