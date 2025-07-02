<template>
  <div class="marking-detail-container">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else-if="error" class="error">
      <el-alert :title="error" type="error" :closable="false" />
      <div class="error-actions">
        <el-button @click="fetchAnswerDetail">重试</el-button>
        <el-button @click="goBack">返回列表</el-button>
      </div>
    </div>
    <div v-else class="marking-detail">
      <div class="header">
        <h2>答案评阅详情</h2>
        <el-button @click="goBack" type="primary" plain>
          返回列表
        </el-button>
      </div>
      
      <el-divider></el-divider>

      <el-card class="question-card">
        <template #header>
          <div class="card-header">
            <span>题目内容</span>
            <span class="score-label">满分: {{ answer.examQuestion?.score || 0 }}分</span>
          </div>
        </template>
        <div class="question-content" v-html="answer.examQuestion?.questionContent"></div>
      </el-card>

      <el-card class="answer-card">
        <template #header>
          <div class="card-header">
            <span>考生答案</span>
            <span class="student-info" v-if="answer.participant?.user">
              考生: {{ answer.participant.user.username }}
            </span>
          </div>
        </template>
        <div class="answer-content" v-html="answer.answerText"></div>
      </el-card>

      <el-card class="marking-card">
        <template #header>
          <div class="card-header">
            <span>评分区域</span>
            <div>
              <el-tag :type="statusType" effect="dark">{{ statusText }}</el-tag>
              <el-tag v-if="answer.markerCount && answer.requiredMarkerCount" type="info" effect="plain" class="ml-2">
                已评阅: {{ answer.markerCount }}/{{ answer.requiredMarkerCount }}
              </el-tag>
            </div>
          </div>
        </template>
        
        <!-- 多人评分记录 -->
        <div v-if="answer.markerScoresWithInfo && answer.markerScoresWithInfo.length > 0" class="marker-scores">
          <h4>评分记录</h4>
          <el-table :data="answer.markerScoresWithInfo" stripe style="width: 100%">
            <el-table-column prop="markerInfo.username" label="评阅人" width="120" />
            <el-table-column prop="score" label="分数" width="80" />
            <el-table-column prop="comments" label="评语" />
            <el-table-column prop="markedAt" label="评阅时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.markedAt) }}
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 评分统计 -->
          <div v-if="answer.markerCount && answer.markerCount > 1" class="score-statistics">
            <div class="statistic-item">
              <span class="statistic-label">平均分:</span>
              <span class="statistic-value">{{ calculateAverageScore() }}</span>
            </div>
            <div class="statistic-item">
              <span class="statistic-label">方差:</span>
              <span class="statistic-value" :class="{'high-variance': answer.needArbitration}">
                {{ answer.scoreVariance?.toFixed(2) || 0 }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 已评阅状态 -->
        <div v-if="answer.status === 'marked'" class="marked-content">
          <div class="score-display">
            <span class="score-label">最终得分:</span>
            <span class="score-value">{{ answer.score }}</span>
          </div>
          <div class="comments-display">
            <span class="comments-label">最终评语:</span>
            <div class="comments-value">{{ answer.comments || '无评语' }}</div>
          </div>
          <div class="marker-info" v-if="answer.marker">
            <span>主评阅人: {{ answer.marker.username }}</span>
            <span>评阅时间: {{ formatDate(answer.markedAt) }}</span>
          </div>
        </div>
        
        <!-- 有争议状态 -->
        <div v-else-if="answer.status === 'disputed'" class="disputed-content">
          <el-alert
            title="此答案存在评分争议，需要仲裁"
            type="warning"
            :closable="false"
            show-icon
          />
          
          <!-- 仲裁信息 -->
          <div v-if="answer.arbitrationInfo" class="arbitration-info">
            <h4>仲裁信息</h4>
            <div class="arbitration-details">
              <p><strong>仲裁状态:</strong> {{ arbitrationStatusText(answer.arbitrationInfo.status) }}</p>
              <p><strong>仲裁原因:</strong> {{ answer.arbitrationInfo.reason }}</p>
              <p v-if="answer.arbitrationInfo.status === 'approved' || answer.arbitrationInfo.status === 'rejected'">
                <strong>仲裁结果:</strong> {{ answer.arbitrationInfo.resolution }}
              </p>
              <p v-if="answer.arbitrationInfo.status === 'approved'">
                <strong>调整后分数:</strong> {{ answer.arbitrationInfo.adjustedScore }}
              </p>
            </div>
          </div>
          
          <!-- 仲裁表单 -->
          <div v-if="isArbitrator && (!answer.arbitrationInfo || answer.arbitrationInfo.status === 'reviewing')" class="arbitration-form">
            <h4>仲裁评分</h4>
            <el-form :model="arbitrationForm" label-position="top">
              <el-form-item label="调整后分数">
                <el-input-number 
                  v-model="arbitrationForm.adjustedScore" 
                  :min="0" 
                  :max="answer.examQuestion?.score || 100" 
                  :step="0.5"
                />
              </el-form-item>
              <el-form-item label="仲裁说明">
                <el-input 
                  v-model="arbitrationForm.resolution" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="请输入仲裁说明"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitArbitration" :loading="submitting">
                  提交仲裁结果
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        
        <!-- 待评分状态 -->
        <div v-else-if="canMark" class="marking-form">
          <el-form :model="markingForm" label-position="top">
            <el-form-item label="分数">
              <el-input-number 
                v-model="markingForm.score" 
                :min="0" 
                :max="answer.examQuestion?.score || 100" 
                :step="0.5"
              />
            </el-form-item>
            <el-form-item label="评语">
              <el-input 
                v-model="markingForm.comments" 
                type="textarea" 
                :rows="4" 
                placeholder="请输入评语"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitMarking" :loading="submitting">
                提交评分
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 无权评分或已评分 -->
        <div v-else-if="hasMarkedByCurrentUser" class="already-marked">
          <el-alert
            title="您已经对此答案进行了评分"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </el-card>

      <el-card class="reference-card">
        <template #header>
          <div class="card-header">
            <span>参考答案与解析</span>
          </div>
        </template>
        <div class="reference-content">
          <div class="explanation" v-if="answer.examQuestion?.explanation">
            <h4>解析:</h4>
            <div v-html="answer.examQuestion.explanation"></div>
          </div>
          <div v-else class="no-explanation">
            暂无解析
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getAnswerDetail, markAnswer, arbitrateAnswer, SubjectiveAnswer, MarkerScore } from '../api/subjectiveAnswer';
import { useUserStore } from '../stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const answerId = computed(() => Number(route.params.id));

const answer = ref<SubjectiveAnswer>({} as SubjectiveAnswer);
const loading = ref(true);
const error = ref('');
const submitting = ref(false);

const markingForm = ref({
  score: 0,
  comments: ''
});

const arbitrationForm = ref({
  adjustedScore: 0,
  resolution: ''
});

// 当前用户是否为仲裁员
const isArbitrator = computed(() => {
  return userStore.currentUser?.role === 'arbitrator' || userStore.currentUser?.role === 'admin';
});

// 当前用户是否可以评分
const canMark = computed(() => {
  // 如果答案不是待评阅或评阅中状态，则不能评分
  if (answer.value.status !== 'pending' && answer.value.status !== 'marking') {
    return false;
  }
  
  // 检查当前用户是否已经评过分
  return !hasMarkedByCurrentUser.value;
});

// 当前用户是否已经评过分
const hasMarkedByCurrentUser = computed(() => {
  if (!answer.value.markerScores || !userStore.currentUser) {
    return false;
  }
  
  return answer.value.markerScores.some(score => score.markerId === userStore.currentUser?.id);
});

// 状态显示
const statusText = computed(() => {
  switch (answer.value.status) {
    case 'pending': return '待评阅';
    case 'marking': return '评阅中';
    case 'marked': return '已评阅';
    case 'disputed': return '有争议';
    case 'arbitrated': return '已仲裁';
    default: return '未知状态';
  }
});

const statusType = computed(() => {
  switch (answer.value.status) {
    case 'pending': return 'info';
    case 'marking': return 'primary';
    case 'marked': return 'success';
    case 'disputed': return 'warning';
    case 'arbitrated': return 'success';
    default: return 'info';
  }
});

// 仲裁状态文本
const arbitrationStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理';
    case 'reviewing': return '审核中';
    case 'approved': return '已批准';
    case 'rejected': return '已拒绝';
    default: return '未知状态';
  }
};

// 计算平均分
const calculateAverageScore = () => {
  if (!answer.value.markerScores || answer.value.markerScores.length === 0) {
    return 0;
  }
  
  const scores = answer.value.markerScores.map(item => parseFloat(item.score.toString()));
  const sum = scores.reduce((acc, score) => acc + score, 0);
  return (sum / scores.length).toFixed(2);
};

// 格式化日期
const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知时间';
  const date = new Date(dateString);
  return date.toLocaleString();
};

// 获取答案详情
const fetchAnswerDetail = async () => {
  loading.value = true;
  error.value = '';
  try {
    answer.value = await getAnswerDetail(answerId.value);
    
    // 如果有仲裁需求，初始化仲裁表单
    if (answer.value.status === 'disputed' && answer.value.score !== null) {
      arbitrationForm.value.adjustedScore = answer.value.score;
    }
  } catch (err: any) {
    error.value = err.response?.data?.message || '获取答案详情失败';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 提交评分
const submitMarking = async () => {
  if (markingForm.value.score < 0) {
    ElMessage.error('分数不能为负数');
    return;
  }
  
  if (answer.value.examQuestion && markingForm.value.score > answer.value.examQuestion.score) {
    ElMessage.error(`分数不能超过题目满分${answer.value.examQuestion.score}分`);
    return;
  }
  
  submitting.value = true;
  try {
    const result = await markAnswer(
      answerId.value, 
      markingForm.value.score, 
      markingForm.value.comments
    );
    ElMessage.success(result.message || '评分成功');
    // 刷新答案详情
    await fetchAnswerDetail();
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '评分提交失败');
    console.error(err);
  } finally {
    submitting.value = false;
  }
};

// 提交仲裁结果
const submitArbitration = async () => {
  if (arbitrationForm.value.adjustedScore < 0) {
    ElMessage.error('分数不能为负数');
    return;
  }
  
  if (answer.value.examQuestion && arbitrationForm.value.adjustedScore > answer.value.examQuestion.score) {
    ElMessage.error(`分数不能超过题目满分${answer.value.examQuestion.score}分`);
    return;
  }
  
  if (!arbitrationForm.value.resolution.trim()) {
    ElMessage.error('请输入仲裁说明');
    return;
  }
  
  submitting.value = true;
  try {
    const result = await arbitrateAnswer(
      answerId.value, 
      arbitrationForm.value.adjustedScore, 
      arbitrationForm.value.resolution
    );
    ElMessage.success(result.message || '仲裁成功');
    // 刷新答案详情
    await fetchAnswerDetail();
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '仲裁提交失败');
    console.error(err);
  } finally {
    submitting.value = false;
  }
};

// 返回列表
const goBack = () => {
  router.push('/marking');
};

onMounted(() => {
  fetchAnswerDetail();
});
</script>
</script>

<style scoped>
.marking-detail {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 1em;
  color: #1976d2;
  margin-right: 20px;
}

.back-button span {
  margin-right: 5px;
}

.loading, .error-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.question-card h2, .answer-card h2, .marking-card h2, .explanation-card h2 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  color: #333;
}

.question-content {
  margin-bottom: 15px;
  line-height: 1.6;
}

.question-meta {
  display: flex;
  justify-content: flex-end;
}

.score-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 5px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.answer-content {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.marked-info, .disputed-info {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 20px;
}

.marked-header, .disputed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status {
  padding: 5px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.status.marked {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.status.disputed {
  background-color: #ffcdd2;
  color: #c62828;
}

.marker-info {
  font-size: 0.9em;
  color: #666;
}

.score-display {
  margin-bottom: 15px;
  font-size: 1.2em;
}

.score-label {
  margin-right: 10px;
}

.score-value {
  font-weight: bold;
  font-size: 1.5em;
  color: #1976d2;
}

.score-total {
  color: #666;
  margin-left: 5px;
}

.comments h3, .dispute-reason h3 {
  margin-top: 15px;
  margin-bottom: 10px;
  font-size: 1em;
  color: #555;
}

.comments-content, .reason-content {
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
  white-space: pre-wrap;
}

.marking-form {
  margin-top: 20px;
}

.marking-form h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1em;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

input[type="number"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 80px;
}

.max-score {
  margin-left: 10px;
  color: #666;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.submit-button {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #1565c0;
}

.submit-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.explanation-content {
  padding: 15px;
  background-color: #fff8e1;
  border-radius: 4px;
  border-left: 4px solid #ffc107;
  line-height: 1.6;
}
</style>