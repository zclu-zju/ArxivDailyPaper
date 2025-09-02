<script setup>
import {ref, watch, onMounted} from "vue";
import {useRoute, useRouter} from "vue-router";

import {queryPapers} from "@/services/queryPapers.js";
import {strToBool, textToImage} from "@/services/utils.js";
import PaperTableSummary from "@/components/PaperTableSummary.vue";
import PaperTableMarks from "@/components/PaperTableMarks.vue";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const kw = ref(route.query.kw);
const subjects = ref(route.query.subjects);

const pageNum = ref(parseInt(route.query.pageNum || 1));
const pageSize = ref(parseInt(route.query.pageSize || 10));
const totalCount = ref(1);

const filters = ref({
  is_read: strToBool(route.query.is_read) || false,
  is_favorite: strToBool(route.query.is_favorite) || false,
  is_uninterested: strToBool(route.query.is_uninterested) || false, // Ignore Uninterested
  is_to_read: strToBool(route.query.is_to_read) || false,
});

const papers = ref([]);
const loadPapers = async () => {
  papers.value.length = 0;
  loading.value = true;
  const data = await queryPapers(
      pageNum.value,
      pageSize.value,
      kw.value,
      subjects.value,
      true,
      filters.value,
  )
  totalCount.value = data.total;
  for (const item of data.items) {
    item.src = textToImage(item.summary);
  }
  papers.value.push(...data.items)
  loading.value = false;
}

const changeQuery = () => {
  router.push({
    name: "Papers",
    query: {
      kw: kw.value,
      subjects: subjects.value,
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      ...filters.value,
    }
  })
}

const previewURL = ref('');
const changePreviewURL = (url) => {
  previewURL.value = url;
}

onMounted(loadPapers);
watch([
  kw, subjects, pageNum, pageSize,
], () => {
  changeQuery();
})
watch(filters, () => {
  pageNum.value = 1
  pageSize.value = 10
  totalCount.value = 1
  changeQuery();
}, {deep: true})
const changePage = (newPageNum) => {
  pageNum.value = newPageNum;
}
</script>

<template>
  <div class="header-op">
    <el-space class="filter-box" style=" "
              v-for="i in 2" :key="i"
    >
      <el-switch v-model="filters.is_read"
                 :active-value="true"
                 :inactive-value="false"
                 active-text="已读"
                 :loading="loading"
      />
      <el-switch v-model="filters.is_favorite"
                 :active-value="true"
                 :inactive-value="false"
                 active-text="收藏"
                 :loading="loading"
      />
      <el-switch v-model="filters.is_uninterested"
                 :active-value="true"
                 :inactive-value="false"
                 active-text="屏蔽"
                 :loading="loading"
      />
    </el-space>
  </div>
  <el-scrollbar style="height: calc(100vh - 180px)">
    <el-table v-loading="loading" :data="papers">
      <el-table-column type="expand">
        <template #default="scope">
          <paper-table-summary
              :row="scope.row"
              @changePreviewURL="changePreviewURL"
          >
          </paper-table-summary>
        </template>
      </el-table-column>
      <el-table-column width="200" label="Marks" align="center">
        <template #default="scope">
          <paper-table-marks :marks="scope.row.marks" :doi="scope.row.doi" :only-reading="true"/>
        </template>
      </el-table-column>
      <el-table-column
          label="Title"
      >
        <template #default="scope">
          <el-link @click="router.push({
              name: 'PaperDetail',
              params: {doi: scope.row.doi},
            })" :style="{'text-decoration': scope.row.marks.is_uninterested? 'line-through':'none'}">
            {{ scope.row.title }}
          </el-link>
          <el-badge
              :is-dot="scope.row.marks.is_read" color="#a0d0d0"
          />
          <el-badge
              :is-dot="scope.row.marks.is_favorite" color="#dca7eb"
          />
          <el-badge
              :is-dot="scope.row.marks.note" color="#eae936"
          />

        </template>
      </el-table-column>
      <el-table-column
          label="Subjects"
          width="200"
      >
        <template #default="scope">
          <el-space>
            <template
                v-for="(subject, index) in scope.row.subjects"
            >
              <el-text truncated><span :class="{'main-subject' : index === 0}"> {{ subject }}; </span></el-text>
            </template>
          </el-space>
        </template>
      </el-table-column>
    </el-table>
  </el-scrollbar>
  <div style="width: 100%; display: flex; justify-content: center;padding: 10px 0 0; border-top: var(--el-border)">
    <el-pagination
        v-if="!loading"
        :total="totalCount"
        :pageSize="pageSize"
        :current-page="pageNum"
        @update:current-page="changePage"
        layout="total, prev, pager, next"
    />
  </div>
  <el-image-viewer
      v-if="previewURL"
      @close="()=>{changePreviewURL('')}"
      :url-list="[previewURL]"
      z-index="9999"
      hide-on-click-modal
  ></el-image-viewer>
</template>

<style scoped>
.header-op {
  display: flex;
  justify-content: space-between;
}
</style>