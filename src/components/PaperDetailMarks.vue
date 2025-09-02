<script setup>
import {ref, watch, defineProps, onMounted} from 'vue'
import {Hide, View, Star, StarFilled} from '@element-plus/icons-vue'
import api from "@/services/axios.js";
import {ElMessage} from "element-plus";
import {updateMarkField} from "@/services/queryMarks.js";

const props = defineProps({
  marks: {
    type: Object,
    required: true,
    default: {
      doi: "",
      is_favorite: false,
      is_read: false,
      is_to_read: false,
      is_uninterested: false,
      note: null,
      rating: 0,
      read_count: 0,
    }
  },
  doi: {
    type: String,
    required: true
  },
  onlyReading: {
    type: Boolean,
    default: false
  },
  col: {
    type: Number,
    default: 1
  }
})
const localMark = ref({...props.marks})

const colors = ref({
  1: '#99A9BF',
  2: '#F7BA2A',
  3: '#f1ba91',
  4: '#f1b17c',
  5: '#ff1500'
})


watch(() => localMark.value.is_favorite, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "is_favorite", newVal)
  }
})

watch(() => localMark.value.is_uninterested, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "is_uninterested", newVal)
  }
})
watch(() => localMark.value.rating, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "rating", newVal)
  }
})

watch(() => localMark.value.note, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "note", newVal)
  }
})

watch(() => localMark.value.is_read, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "is_read", newVal)
  }
})

watch(() => localMark.value.progress, (newVal, oldVal) => {
  if (oldVal !== undefined) {
    updateMarkField(props.doi, "progress", newVal)
  }
})


</script>

<template>
  <el-descriptions :column="col" border style="">
    <el-descriptions-item label="收藏">
      <div class="collection">
        <el-switch v-model="localMark.is_favorite"
                   :active-value="true"
                   :inactive-value="false"
                   :active-action-icon="StarFilled"
                   :inactive-action-icon="Star"
                   style="--el-switch-on-color: #E6A23C"
        />
      </div>
    </el-descriptions-item>
    <el-descriptions-item label="评分">
      <div class="mark-rate">
        <el-rate
            :disabled="onlyReading"
            :colors="colors"
            v-model="localMark.rating"
        ></el-rate>
      </div>
    </el-descriptions-item>
    <el-descriptions-item label="屏蔽">
      <div class="mark-is_uninterested">
        <el-switch v-model="localMark.is_uninterested"
                   :active-value="true"
                   :inactive-value="false"
                   :active-action-icon="Hide"
                   :inactive-action-icon="View"
                   style="--el-switch-on-color: #EAECF0; --el-switch-off-color: #13CE66"
        />
      </div>
    </el-descriptions-item>
  </el-descriptions>
</template>

<style scoped>

</style>