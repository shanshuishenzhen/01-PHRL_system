<template>
  <div class="home">
    <h1>欢迎来到阅卷中心</h1>
    
    <div v-if="userStore.isAdmin" class="admin-notice">
      <h2>管理员提示</h2>
      <p>尊敬的管理员，您可以访问所有阅卷功能。</p>
      <p>您可以通过点击导航栏的"阅卷中心"开始阅卷工作。</p>
    </div>
    
    <div v-else-if="userStore.isTeacher" class="teacher-info">
      <p>您可以通过点击导航栏的"阅卷中心"开始阅卷工作。</p>
    </div>
    
    <div v-else class="student-info">
      <p>学生用户可以查看自己的考试成绩和申请仲裁。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../stores/user';

const userStore = useUserStore();
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 50px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  padding: 20px;
}

.admin-notice {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 5px;
  color: #721c24;
}

.teacher-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 5px;
  color: #155724;
}

.student-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #cce5ff;
  border: 1px solid #b8daff;
  border-radius: 5px;
  color: #004085;
}
</style>