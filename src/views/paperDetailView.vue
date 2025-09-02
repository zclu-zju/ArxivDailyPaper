<script setup>
import {ref, inject, watch, onBeforeMount} from "vue"
import {useRoute} from "vue-router";

import {getPaperDetail} from "@/services/queryPapers.js";
import LoadingSkeleton from "@/components/loadingSkeleton.vue";
import {textToImage} from "@/services/utils.js";
import PaperDetailMarks from "@/components/PaperDetailMarks.vue";
import {updateNote} from "@/services/queryMarks.js";

const route = useRoute();
const loading = ref(true);
const showAbstract = ref(false);

const doi = route.params.doi;

const detail = ref({
  id: '',
  doi: '',
  url: '',
  title: '',
  authors: [],
  subjects: [],
  summary: '',
  created_at: '',
  marks: ''
});

const loadPaper = async () => {
  detail.value = await getPaperDetail(doi);
  detail.value.src = textToImage(detail.value.summary)
  detail.value.marks.note = detail.value.marks.note || "";
  document.title = detail.value.title;
  loading.value = false;
}


const col = ref(0);
const innerWidth = inject("innerWidth");
const updateCol = () => {
  if (innerWidth.value > 1280) {
    col.value = 3;
  } else if (innerWidth.value > 1100) {
    col.value = 2;
  } else {
    col.value = 1;
  }
}

watch(innerWidth, updateCol);
onBeforeMount(() => {
  loadPaper();
  updateCol();
});

const saveNote = async () => {
  updateNote(doi, detail.value.marks.note);
}
</script>

<template>
  <el-descriptions
      :column="col"
      direction="vertical"
      border
      size="large"
  >
    <el-descriptions-item label="Paper Marks" :span="col">
      <paper-detail-marks
          v-if="!loading" :doi="detail.doi" :marks="detail.marks"
          :col="col"
      />
    </el-descriptions-item>
    <el-descriptions-item label="Paper Title" :span="col">
      <loading-skeleton variant="p" :loading="loading">
        <el-text>
          {{ detail.title }}
        </el-text>
      </loading-skeleton>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Link">
      <loading-skeleton variant="p" :loading="loading">
        <el-link :href="detail.url" type="info">
          {{ detail.url }}
        </el-link>
      </loading-skeleton>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Authors">
      <loading-skeleton :loading="loading" variant="p">
        <el-text truncated> {{ detail.authors.join(", ") }}</el-text>
      </loading-skeleton>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Subjects" :span="col===2? 2: 1">
      <loading-skeleton :loading="loading" variant="rect">
        <el-space>
          <template
              v-for="(subject, index) in detail.subjects"
          >
            <el-text><span :class="{'main-subject' : index === 0}"> {{ subject }}; </span></el-text>
          </template>
        </el-space>
      </loading-skeleton>
    </el-descriptions-item>
    <el-descriptions-item :span="col">
      <template #label>
        <span class="desc-label-btn" @click="showAbstract=true">Paper Abstract</span>
      </template>
      <loading-skeleton :loading="loading" variant="rect">
        <el-text>{{ detail.summary }}</el-text>
      </loading-skeleton>
    </el-descriptions-item>
    <el-descriptions-item label="Paper Note" :span="col">
      <loading-skeleton :loading="loading" :rows="2">
        <el-input
            type="textarea"
            v-model="detail.marks.note"
            show-word-limit
            maxlength="2000"
            :autosize="{
              minRows: 5,
              maxRows: 20
            }"
            resize="none"
            @keydown="(e)=>{
              if(e.keyCode === 83) {
                if(e.ctrlKey) {
                  e.preventDefault();
                  saveNote();
                }
              }
            }"
        ></el-input>
      </loading-skeleton>
      <div style="width: 100%;display: flex;justify-content: space-between; margin-top: 10px;">
        <el-button type="success" plain
                   @click="saveNote"
        >Save</el-button>
      </div>
    </el-descriptions-item>
  </el-descriptions>

  <el-image-viewer
      v-if="showAbstract"
      @close="showAbstract = false"
      :url-list="[detail.src]"
      z-index="9999"
      hide-on-click-modal
  ></el-image-viewer>
</template>

<style scoped>

</style>