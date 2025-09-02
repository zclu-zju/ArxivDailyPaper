<script setup>
import {ref, watch, onMounted} from "vue";
import {Sunny, Moon} from '@element-plus/icons-vue';

const isDark = ref(false);

const switchBtnClassName = ref("switch-btn-dark");

watch(isDark, () => {
  switchBtnClassName.value = isDark.value ? 'switch-btn-white' : 'switch-btn-dark'

  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }

  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
})

onMounted(() => {
  const theme = localStorage.getItem('theme')
  if (theme === 'dark') {
    isDark.value = true
  }
})
</script>
<template>
  <el-switch
      :class="switchBtnClassName"
      v-model="isDark"
      style="--el-switch-off-color: #F2F2F2;--el-switch-on-color: #2C2C2C;"
  >
    <template #inactive-action>
      <el-icon color="#000">
        <Sunny/>
      </el-icon>
    </template>
    <template #active-action>
      <el-icon color="#fff">
        <Moon/>
      </el-icon>
    </template>
  </el-switch>
</template>

<style scoped>
.switch-btn-dark ::v-deep .el-switch__action {
  background: #c4c4c4;
}

.switch-btn-white ::v-deep .el-switch__action {
  background: #525252;
}
</style>