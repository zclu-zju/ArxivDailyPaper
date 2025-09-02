<script setup>
import {useRoute, useRouter} from "vue-router";
import {ref, watch, inject, onBeforeMount} from "vue";

import logo from "@/assets/logo.png"
import SwitchDarkButton from "@/components/SwitchDarkButton.vue";

const router = useRouter();
const route = useRoute();
const activeIndex = ref(route.path);
watch(route, (newRoute) => {
  activeIndex.value = newRoute.path;
})
const changeActiveIndex = (path) => {
  router.push(path);
}

const menuItems = inject("menuItems")

const tourOpen = ref(true)
const scholarRef = ref(null)
const homeRef = ref(null)
const contactRef = ref(null)

const handleTourClose = () => {
  localStorage.setItem('tourSeen', 'true')
  tourOpen.value = false
}

onBeforeMount(() => {
  if (localStorage.getItem('tourSeen') === 'true') {
    tourOpen.value = false
  }
})

const innerWidth = inject("innerWidth");
</script>

<template>
  <el-menu
      mode="horizontal"
      :default-active="activeIndex"
      style="align-items: center;"
      :ellipsis="innerWidth <= 600"
  >
    <el-menu-item class="logo-menu">
      <el-image :src="logo"
                fit="contain"
                style="height: var(--el-header-height);"
                @click="router.push({name: 'home'})"
      ></el-image>
    </el-menu-item>
    <el-menu-item
        v-for="menuItem in menuItems"
        :key="menuItem.path"
        :index="menuItem.path"
        @click="changeActiveIndex(menuItem.path)"
    >
      {{ menuItem.title }}
    </el-menu-item>
    <div style="padding-right: 1em;">
      <SwitchDarkButton/>
    </div>
    <el-menu-item>
      <el-link
          type="primary" :underline="false" target="_blank"
          href="https://scholar.google.com/citations?user=byXIEVMAAAAJ&hl=en"
          ref="scholarRef"
      >
        Google Scholar
      </el-link>
    </el-menu-item>
    <el-menu-item>
      <el-link
          href="https://zcluu.github.io/#/"
          target="_blank"
          :underline="false"
          ref="homeRef"
      >HomePage
      </el-link>
    </el-menu-item>
    <el-menu-item>
      <el-link
          href="mailto:zclu@zju.edu.cn" :underline="false"
          ref="contactRef"
      >Contact Me
      </el-link>
    </el-menu-item>
  </el-menu>
  <el-tour v-model="tourOpen" @close="handleTourClose">
    <el-tour-step
        :target="scholarRef?.$el"
        title="Google Scholar"
    >
      Check out my academic profile
    </el-tour-step>

    <el-tour-step
        :target="homeRef?.$el"
        title="Home Page"
    >
      Visit my personal homepage
    </el-tour-step>

    <el-tour-step
        :target="contactRef?.$el"
        title="Contact"
    >Send me an email
    </el-tour-step>
  </el-tour>
</template>

<style scoped>

.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

.logo-menu {
  --el-menu-hover-bg-color: var(--el-color-white);
  --el-menu-base-level-padding: 10px;
}
</style>