<script setup>
import {ref} from "vue";
import {useRoute} from "vue-router";

import api from "@/services/axios.js"
import {ElMessage} from "element-plus";

const route = useRoute();
const username = ref("");
const password = ref("");

const login = () => {
  api.post("/login", {
    username: username.value, password: password.value
  }).then((res) => {
    ElMessage.success("Login successful!");
    localStorage.setItem("authToken", res.access_token);
  }).catch((err) => {
    ElMessage.error("Login failed!")
  })
}
</script>

<template>
  <el-row style="justify-content: center;">
    <el-col
        :xs="24"
        :md="20"
        :lg="12"
    >
      <el-card shadow="never" style="margin-top: 10vh;">
        <el-form label-position="top" size="large" @submit.prevent="login">
          <el-form-item label="username">
            <el-input v-model="username"></el-input>
          </el-form-item>
          <el-form-item label="password">
            <el-input v-model="password"
                      type="password"
            ></el-input>
          </el-form-item>
          <el-form-item style="margin-bottom: 0;">
            <div style="width: 100%; display: flex; justify-content: end;">
              <el-button size="large" type="success" plain
                         @click="login">
                Login
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>

</style>