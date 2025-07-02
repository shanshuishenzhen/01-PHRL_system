<template>
  <div class="marking-view">
    <h1>阅卷中心</h1>
    
    <div class="exam-selector">
      <label for="exam-select">选择考试：</label>
      <select id="exam-select" v-model="selectedExamId" @change="loadAnswers">
        <option value="">请选择考试</option>
        <option v-for="exam in exams" :key="exam.id" :value="exam.id">
          {{ exam.examName }}
        </option>
      </select>
    </div>
    
    <div class="tab-container">
      <div class="tabs">
        <button 
          :class="{ active: activeTab === 'pending' }" 
          @click="setActiveTab('pending')"
        >
          待阅卷 <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
        </button>
        <button 
          :class="{ active: activeTab === 'marked' }" 
          @click="setActiveTab('marked')"
        >
          已阅卷
        </button>
      </div>
      
      <div class="tab-content">
        <!-- 待阅卷列表 -->
        <div v-if="activeTab === 'pending'" class="answer-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="pendingAnswers.length === 0" class="empty-state">
            暂无待阅卷答案
          </div>
          <div v-else class="answer-cards">
            <div 
              v-for="answer in pendingAnswers" 
              :key="answer.id" 
              class="answer-card"
              @click="goToMarkingDetail(answer.id)"
            >
              <div class="question-content" v-html="answer.examQuestion?.questionContent"></div>
              <div class="answer-preview">
                <strong>答案预览：</strong>
                <span>{{ truncateText(answer.answerText, 100) }}</span>
              </div>
              <div class="card-footer">
                <span class="status pending">待阅卷</span>
                <span class="score-info">满分: {{ answer.examQuestion?.score }}分</span>
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <div v-if="pendingAnswers.length > 0" class="pagination">
            <button 
              :disabled="pendingPage === 1" 
              @click="changePendingPage(pendingPage - 1)"
            >
              上一页
            </button>
            <span>{{ pendingPage }} / {{ pendingTotalPages }}</span>
            <button 
              :disabled="pendingPage === pendingTotalPages" 
              @click="changePendingPage(pendingPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
        
        <!-- 已阅卷列表 -->
        <div v-if="activeTab === 'marked'" class="answer-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="markedAnswers.length === 0" class="empty-state">
            暂无已阅卷答案
          </div>
          <div v-else class="answer-cards">
            <div 
              v-for="answer in markedAnswers" 
              :key="answer.id" 
              class="answer-card"
              @click="goToMarkingDetail(answer.id)"
            >
              <div class="question-content" v-html="answer.examQuestion?.questionContent"></div>
              <div class="answer-preview">
                <strong>答案预览：</strong>
                <span>{{ truncateText(answer.answerText, 100) }}</span>
              </div>
              <div class="card-footer">
                <span :class="['status', answer.status]">{{ getStatusText(answer.status) }}</span>
                <span class="score-info">
                  得分: {{ answer.score }} / {{ answer.examQuestion?.score }}分
                </span>
              </div>
              <div class="marker-info">
                评阅人: {{ answer.marker?.username || '未知' }} | 
                评阅时间: {{ formatDate(answer.markedAt) }}
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <div v-if="markedAnswers.length > 0" class="pagination">
            <button 
              :disabled="markedPage === 1" 
              @click="changeMarkedPage(markedPage - 1)"
            >
              上一页
            </button>
            <span>{{ markedPage }} / {{ markedTotalPages }}</span>
            <button 
              :disabled="markedPage === markedTotalPages" 
              @click="changeMarkedPage(markedPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getPendingAnswers, getMarkedAnswers } from '../api/subjectiveAnswer';
import type { SubjectiveAnswer } from '../api/subjectiveAnswer';
import { getExams } from '../api/exam';

export default defineComponent({
  name: 'MarkingView',
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const exams = ref<any[]>([]);
    const selectedExamId = ref<number | ''>('');
    const activeTab = ref('pending');
    
    // 待阅卷数据
    const pendingAnswers = ref<SubjectiveAnswer[]>([]);
    const pendingCount = ref(0);
    const pendingPage = ref(1);
    const pendingTotalPages = ref(1);
    
    // 已阅卷数据
    const markedAnswers = ref<SubjectiveAnswer[]>([]);
    const markedPage = ref(1);
    const markedTotalPages = ref(1);
    
    // 加载考试列表
    const loadExams = async () => {
      try {
        console.log('开始加载考试列表...');
        const response = await getExams(1, 10, 'published');
        console.log('考试列表响应:', response);
        exams.value = response.data;
        console.log('考试列表加载成功:', exams.value);
      } catch (error) {
        console.error('加载考试列表失败:', {
          error: error as Error,
          response: (error as any).response,
          config: (error as any).config
        });
      }
    };
    
    // 加载答案列表
    const loadAnswers = async () => {
      if (!selectedExamId.value) return;
      
      loading.value = true;
      try {
        if (activeTab.value === 'pending') {
          await loadPendingAnswers();
        } else {
          await loadMarkedAnswers();
        }
      } catch (error) {
        console.error('加载答案列表失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 加载待阅卷答案
    const loadPendingAnswers = async () => {
      if (!selectedExamId.value) return;
      
      try {
        const response = await getPendingAnswers(
          selectedExamId.value as number, 
          pendingPage.value
        );
        
        pendingAnswers.value = response.data;
        pendingCount.value = response.total;
        pendingTotalPages.value = response.totalPages;
      } catch (error) {
        console.error('加载待阅卷答案失败:', error);
      }
    };
    
    // 加载已阅卷答案
    const loadMarkedAnswers = async () => {
      if (!selectedExamId.value) return;
      
      try {
        const response = await getMarkedAnswers(
          selectedExamId.value as number, 
          markedPage.value
        );
        
        markedAnswers.value = response.data;
        markedTotalPages.value = (response as any).totalPages;
      } catch (error) {
        console.error('加载已阅卷答案失败:', error);
      }
    };
    
    // 切换标签页
    const setActiveTab = (tab: string) => {
      activeTab.value = tab;
      loadAnswers();
    };
    
    // 切换待阅卷分页
    const changePendingPage = (page: number) => {
      pendingPage.value = page;
      loadPendingAnswers();
    };
    
    // 切换已阅卷分页
    const changeMarkedPage = (page: number) => {
      markedPage.value = page;
      loadMarkedAnswers();
    };
    
    // 跳转到阅卷详情页
    const goToMarkingDetail = (answerId: number) => {
      router.push(`/marking/${answerId}`);
    };
    
    // 格式化日期
    const formatDate = (dateString: string | null) => {
      if (!dateString) return '未知';
      return new Date(dateString).toLocaleString();
    };
    
    // 截断文本
    const truncateText = (text: string, maxLength: number) => {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };
    
    // 获取状态文本
    const getStatusText = (status: string) => {
      const statusMap: Record<string, string> = {
        pending: '待阅卷',
        marked: '已阅卷',
        disputed: '有争议'
      };
      return statusMap[status] || status;
    };
    
    onMounted(() => {
      loadExams();
    });
    
    return {
      loading,
      exams,
      selectedExamId,
      activeTab,
      pendingAnswers,
      pendingCount,
      pendingPage,
      pendingTotalPages,
      markedAnswers,
      markedPage,
      markedTotalPages,
      loadAnswers,
      setActiveTab,
      changePendingPage,
      changeMarkedPage,
      goToMarkingDetail,
      formatDate,
      truncateText,
      getStatusText
    };
  }
});
</script>

<style scoped>
.marking-view {
  padding: 20px;
}

.exam-selector {
  margin-bottom: 20px;
}

select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  min-width: 200px;
}

.tab-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.tabs {
  display: flex;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.tabs button {
  padding: 12px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  position: relative;
}

.tabs button.active {
  background-color: white;
  border-bottom: 2px solid #1976d2;
}

.badge {
  display: inline-block;
  background-color: #f44336;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  margin-left: 5px;
}

.tab-content {
  padding: 20px;
  background-color: white;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.answer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.answer-card {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 15px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.answer-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-content {
  font-weight: 500;
  margin-bottom: 10px;
  max-height: 80px;
  overflow: hidden;
}

.answer-preview {
  margin-bottom: 10px;
  color: #555;
  font-size: 0.9em;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.status {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.status.pending {
  background-color: #ffecb3;
  color: #ff8f00;
}

.status.marked {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.status.disputed {
  background-color: #ffcdd2;
  color: #c62828;
}

.score-info {
  font-size: 0.9em;
  color: #555;
}

.marker-info {
  margin-top: 10px;
  font-size: 0.8em;
  color: #777;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.pagination button {
  padding: 5px 10px;
  border: 1px solid #ccc;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>