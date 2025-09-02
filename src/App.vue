<script setup>
import {RouterView} from 'vue-router'
import {ref, watch, onBeforeMount, onBeforeUnmount, provide} from "vue";
import HeaderMenu from "@/components/HeaderMenu.vue";

const innerWidth = ref(window.innerWidth);

onBeforeMount(() => {
  window.addEventListener("resize", () => {
    innerWidth.value = window.innerWidth;
  })
})
onBeforeUnmount(() => {
  window.removeEventListener("resize", () => {
  })
})

const mainBoxHeight = ref(window.innerHeight - 100);
console.log(mainBoxHeight.value)

provide("innerWidth", innerWidth)
</script>

<template>
  <el-container>
    <el-header style="padding: 0; width: 100%;">
      <header-menu/>
    </el-header>
    <el-main>
      <el-scrollbar :max-height="mainBoxHeight">
        <RouterView :key="$route.fullPath"/>
      </el-scrollbar>
    </el-main>
  </el-container>
</template>

<style scoped>
.el-main {
  --el-main-padding: 10px;
}
</style>
