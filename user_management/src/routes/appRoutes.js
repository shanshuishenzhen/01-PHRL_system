import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ExamList from '../components/ExamManagement/ExamList';
import UserList from '../components/UserManagement/UserList';

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<UserList />} />
    <Route path="/users" element={<UserList />} />
    <Route path="/exams" element={<ExamList />} />
  </Routes>
);

export default AppRoutes;