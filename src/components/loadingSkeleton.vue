<script setup>
import {ref, defineProps} from "vue";

const props = defineProps({
  loading: {
    default: true,
    type: Boolean,
    required: true,
  },
  rows: {
    default: 5,
    type: Number,
  },
  animated: {
    default: true,
    type: Boolean,
  },
  variant: {
    type: String,
    default: null
  }
})
</script>

<template>
  <div class="loading-skeleton">
    <el-skeleton :rows="props.rows" :animated="props.animated" v-if="props.loading"
                 :throttle="100"
    >
      <template #template v-if="props.variant">
        <el-skeleton-item :variant="props.variant"></el-skeleton-item>
      </template>
    </el-skeleton>
    <slot name="default" v-else></slot>
  </div>
</template>

<style scoped>

</style>