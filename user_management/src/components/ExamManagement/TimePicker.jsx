import { DateTimePicker } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

export default function ExamTimePicker({ label, value, onChange }) {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DateTimePicker
        label={label}
        value={value}
        onChange={onChange}
        format="YYYY/MM/DD HH:mm"
        disablePast
      />
    </LocalizationProvider>
  );
}