import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Alert,
} from '@mui/material';
import { importUsers } from '../../services/userService';

function UserImport({ open, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [importing, setImporting] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('请选择CSV文件');
    }
  };

  const handleImport = async () => {
    if (!file) return;

    try {
      setImporting(true);
      const formData = new FormData();
      formData.append('file', file);
      await importUsers(formData);
      onSuccess();
      onClose();
    } catch (error) {
      setError(error.message);
    } finally {
      setImporting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>批量导入用户</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          请选择CSV文件进行用户批量导入。文件必须包含以下字段：
          用户名、姓名、角色(1考生2考评员3管理员)、密码、手机号、邮箱、单位、身份证号、性别、地址、备注、状态(1正常2待审3冻结)、创建时间、更新时间
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          onClick={() => {
            // 添加 BOM 标记以确保 Excel 正确识别 UTF-8 编码
            const BOM = '\uFEFF';
            // 使用与后端完全匹配的字段名
            const headers = [
              'username',
              'trueName',
              'role',        // 修改 roleId 为 role
              'password',
              'tel',
              'email',
              'unitName',
              'idCard',
              'sex',
              'address',
              'remark',
              'status',
              'createTime',
              'updateTime'
            ].join(',');
            
            // 示例数据，添加创建时间和更新时间
            const currentDate = new Date().toLocaleDateString('zh-CN').split('/').join('-');
            const rows = [
              // 按照字段顺序：username,trueName,role,password,tel,email,unitName,idCard,sex,address,remark,status,createTime,updateTime
              `zhangsan,张三,1,123456,13800138000,zhangsan@example.com,测试单位,110101199001011234,男,北京市海淀区,无,1,${currentDate},${currentDate}`,
              `lisi,李四,2,123456,13900139000,lisi@example.com,测试学校,110101199001011235,女,北京市朝阳区,无,1,${currentDate},${currentDate}`
            ];
            
            const csvContent = BOM + [headers, ...rows].join('\n');
            
            const blob = new Blob([csvContent], { 
              type: 'text/csv;charset=utf-8'
            });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'user_import_template.csv';
            link.click();
            
            // 清理 URL 对象
            URL.revokeObjectURL(link.href);
          }}
          style={{ marginBottom: '10px' }}
        >
          下载示例文件
        </Button>
        <input
          accept=".csv"
          type="file"
          onChange={handleFileChange}
          style={{ margin: '20px 0' }}
        />
        {error && (
          <Alert severity="error" style={{ marginTop: 10 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button
          onClick={handleImport}
          variant="contained"
          color="primary"
          disabled={!file || importing}
        >
          {importing ? '导入中...' : '开始导入'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default UserImport;