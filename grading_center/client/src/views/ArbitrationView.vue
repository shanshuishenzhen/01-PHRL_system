<template>
  <div class="arbitration-container">
    <div class="header">
      <h2>评分仲裁</h2>
    </div>
    
    <el-divider></el-divider>
    
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="error" class="error">
      <el-alert :title="error" type="error" :closable="false" />
      <div class="error-actions">
        <el-button @click="fetchDisputedAnswers">重试</el-button>
      </div>
    </div>
    
    <div v-else class="arbitration-content">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="考试">
            <el-select v-model="filterForm.examId" placeholder="选择考试" clearable @change="handleExamChange">
              <el-option 
                v-for="exam in exams" 
                :key="exam.id" 
                :label="exam.title" 
                :value="exam.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
              <el-option label="待处理" value="pending"></el-option>
              <el-option label="审核中" value="reviewing"></el-option>
              <el-option label="已批准" value="approved"></el-option>
              <el-option label="已拒绝" value="rejected"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchDisputedAnswers">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 仲裁列表 -->
      <div class="arbitration-list">
        <el-table 
          v-if="disputedAnswers.length > 0" 
          :data="disputedAnswers" 
          border 
          stripe
          style="width: 100%"
        >
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="examTitle" label="考试" width="180"></el-table-column>
          <el-table-column prop="questionContent" label="题目" :show-overflow-tooltip="true"></el-table-column>
          <el-table-column prop="participantName" label="考生" width="120"></el-table-column>
          <el-table-column prop="scoreInfo" label="评分情况" width="180">
            <template #default="scope">
              <div>
                <el-tooltip :content="`方差: ${scope.row.scoreVariance?.toFixed(2) || 0}`" placement="top">
                  <div>
                    <span>平均分: {{ scope.row.averageScore || 0 }}</span>
                    <el-progress 
                      :percentage="(scope.row.averageScore / scope.row.maxScore) * 100" 
                      :format="() => `${scope.row.averageScore}/${scope.row.maxScore}`"
                    ></el-progress>
                  </div>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="arbitrationStatus" label="仲裁状态" width="100">
            <template #default="scope">
              <el-tag :type="getArbitrationStatusType(scope.row.arbitrationStatus)">
                {{ getArbitrationStatusText(scope.row.arbitrationStatus) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewArbitrationDetail(scope.row.id)"
              >查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-else description="暂无需要仲裁的答案"></el-empty>
        
        <!-- 分页 -->
        <div class="pagination" v-if="total > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          ></el-pagination>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getExams } from '../api/exam';
import { getDisputedAnswers, SubjectiveAnswer } from '../api/subjectiveAnswer';

const router = useRouter();

const loading = ref(true);
const error = ref('');
const exams = ref([]);
const disputedAnswers = ref<SubjectiveAnswer[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

const filterForm = reactive({
  examId: null as number | null,
  status: '' as string
});

// 获取考试列表
const fetchExams = async () => {
  try {
    exams.value = await getExams();
  } catch (err: any) {
    console.error('获取考试列表失败:', err);
    ElMessage.error('获取考试列表失败');
  }
};

// 获取有争议的答案列表
const fetchDisputedAnswers = async () => {
  loading.value = true;
  error.value = '';
  try {
    const result = await getDisputedAnswers({
      page: currentPage.value,
      limit: pageSize.value,
      examId: filterForm.examId,
      status: filterForm.status || undefined
    });
    
    disputedAnswers.value = result.items;
    total.value = result.total;
  } catch (err: any) {
    error.value = err.response?.data?.message || '获取有争议答案列表失败';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 处理考试变更
const handleExamChange = () => {
  currentPage.value = 1;
  fetchDisputedAnswers();
};

// 重置筛选条件
const resetFilter = () => {
  filterForm.examId = null;
  filterForm.status = '';
  currentPage.value = 1;
  fetchDisputedAnswers();
};

// 处理页码变更
const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchDisputedAnswers();
};

// 处理每页条数变更
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchDisputedAnswers();
};

// 获取仲裁状态文本
const getArbitrationStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理';
    case 'reviewing': return '审核中';
    case 'approved': return '已批准';
    case 'rejected': return '已拒绝';
    default: return '未知状态';
  }
};

// 获取仲裁状态类型
const getArbitrationStatusType = (status: string) => {
  switch (status) {
    case 'pending': return 'info';
    case 'reviewing': return 'warning';
    case 'approved': return 'success';
    case 'rejected': return 'danger';
    default: return 'info';
  }
};

// 查看仲裁详情
const viewArbitrationDetail = (answerId: number) => {
  router.push(`/marking/${answerId}`);
};

onMounted(() => {
  fetchExams();
  fetchDisputedAnswers();
});
</script>

<style scoped>
.arbitration-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.arbitration-list {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.error-actions {
  margin-top: 20px;
}
</style>