<script setup>
import {defineProps, defineEmits} from "vue";

const props = defineProps({
  row: {
    type: Object,
    required: true,
  }
})

const emits = defineEmits(["changePreviewURL"]);
const changePreviewURL = (url) => {
  emits("changePreviewURL", url);
}
</script>

<template>
  <el-descriptions
      :column="3"
      direction="vertical"
      border
      size="large"
  >
    <el-descriptions-item label="Paper Title" :span="3">
      <el-text>
        {{ row.title }}
      </el-text>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Link">
      <el-link :href="row.url" type="info">
        {{ row.url }}
      </el-link>
    </el-descriptions-item>
    <el-descriptions-item
        label="Paper Authors"
    >
      <el-text truncated> {{ row.authors.join(", ") }}</el-text>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Subjects">
      <el-space>
        <template
            v-for="(subject, index) in row.subjects"
        >
          <el-text><span :class="{'main-subject' : index === 0}"> {{ subject }}; </span></el-text>
        </template>
      </el-space>
    </el-descriptions-item>
    <el-descriptions-item :span="3">
      <template #label>
              <span class="desc-label-btn" @click="()=>{
                changePreviewURL(row.src);
              }">Paper Abstract</span>
      </template>
      <el-text>{{ row.summary }}</el-text>
    </el-descriptions-item>
  </el-descriptions>

</template>

<style scoped>
</style>