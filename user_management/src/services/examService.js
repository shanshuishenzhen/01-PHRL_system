export const fetchExams = async () => {
  try {
    const response = await axios.get('/api/exams');
    return response.data;
  } catch (error) {
    handleServiceError(error, '获取考试列表失败');
  }
};

export const validateExamTime = (start, end) => {
  if (start >= end) {
    throw new Error('考试结束时间必须晚于开始时间');
  }
  if (end.diff(start, 'hour') > 24) {
    throw new Error('考试时长不能超过24小时');
  }
};

// 在createExam方法中添加校验
const createExam = async (examData) => {
  validateExamTime(examData.startTime, examData.endTime);
  // 包含考试基本信息校验
  if (!examData.examName) {
    throw new Error('考试名称不能为空');
  }
  // ...其他创建逻辑
};