import ExamTimePicker from './TimePicker';

export default function ExamForm() {
  const [examTimes, setExamTimes] = useState({
    start: null,
    end: null
  });

  return (
    <form>
      <ExamTimePicker
        label="考试开始时间"
        value={examTimes.start}
        onChange={(newValue) => setExamTimes(prev => ({...prev, start: newValue}))}
      />
      <ExamTimePicker
        label="考试结束时间"
        value={examTimes.end}
        onChange={(newValue) => setExamTimes(prev => ({...prev, end: newValue}))}
      />
    </form>
  );
}