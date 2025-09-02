<script setup>
import {ref, defineProps} from 'vue'
import {CollectionTag, Document} from '@element-plus/icons-vue'

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

</script>

<template>
  <el-space style="width: 100%;">
    <div class="mark-favorite">
      <el-tooltip :content="localMark.is_favorite?'Remove from collection': 'Add to collection'">
        <el-icon
            size="large"
            @click="()=> {
              if(!onlyReading){
                localMark.is_favorite = !localMark.is_favorite
              }
            }"
            :color="localMark.is_favorite?'rgb(245,153,17)':''"
        >
          <CollectionTag/>
        </el-icon>
      </el-tooltip>
    </div>
    <div class="mark-rate">
      <el-rate
          :disabled="onlyReading"
          :colors="colors"
          v-model="localMark.rating"
      ></el-rate>
    </div>
    <div class="mark-note">
      <el-tooltip content="Read Note" v-if="localMark.note">
        <el-icon size="large">
          <Document/>
        </el-icon>
      </el-tooltip>
    </div>
  </el-space>
</template>

<style scoped>
.mark-favorite, .mark-note {
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  padding-top: 2px;
}
</style>