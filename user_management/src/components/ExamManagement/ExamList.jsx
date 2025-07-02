import { useState, useEffect } from 'react';
import { fetchExams } from '../../services/examService';

export default function ExamList() {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchExams();
        setExams(data);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <div className="exam-list">
      {loading ? (
        <div>加载考试数据中...</div>
      ) : (
        <table>
          {/* 表格内容实现 */}
        </table>
      )}
    </div>
  );
}