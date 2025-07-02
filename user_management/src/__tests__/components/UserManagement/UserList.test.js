import { render, screen } from '@testing-library/react';
import UserList from '../../../components/UserManagement/UserList';

describe('UserList Component', () => {
  test('渲染空状态时显示加载提示', () => {
    render(<UserList />);
    expect(screen.getByText(/加载中.../i)).toBeInTheDocument();
  });
});